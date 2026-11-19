import hashlib
import hmac
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from .. import config
from ..auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from ..database import get_session
from ..models import EmailCode, Role, User, utcnow
from ..schemas import (
    ForgotPasswordRequest,
    ResendRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserRead,
    VerifyEmailRequest,
)
from ..services import mailer

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash(user_id: int, purpose: str, code: str) -> str:
    return hashlib.sha256(f"{user_id}:{purpose}:{code}".encode()).hexdigest()


def _get_user(session: Session, email: str):
    return session.exec(select(User).where(User.email == email.strip().lower())).first()


def _issue_code(session: Session, user: User, purpose: str) -> bool:
    """Create a fresh 6-digit code and email it. Returns False if asked again too soon."""
    now = utcnow()
    old_rows = session.exec(
        select(EmailCode).where(EmailCode.user_id == user.id, EmailCode.purpose == purpose)
    ).all()
    for old in old_rows:
        if (now - old.created_at).total_seconds() < config.RESEND_COOLDOWN_SECONDS:
            return False
        session.delete(old)
    code = f"{secrets.randbelow(1_000_000):06d}"
    session.add(
        EmailCode(
            user_id=user.id,
            purpose=purpose,
            code_hash=_hash(user.id, purpose, code),
            expires_at=now + timedelta(minutes=config.CODE_TTL_MINUTES),
        )
    )
    session.commit()
    subject = "Your FixMyCity verification code" if purpose == "verify" else "Your FixMyCity password reset code"
    mailer.send_email(
        user.email,
        subject,
        f"Hello {user.name},\n\nYour code is: {code}\n\n"
        f"It expires in {config.CODE_TTL_MINUTES} minutes. If you did not ask for it, ignore this email.\n\n- FixMyCity",
    )
    return True


def _check_code(session: Session, user: User, purpose: str, code: str) -> None:
    row = session.exec(
        select(EmailCode).where(EmailCode.user_id == user.id, EmailCode.purpose == purpose)
    ).first()
    if not row or row.expires_at < utcnow():
        raise HTTPException(400, "Code expired or not found. Please request a new one.")
    if row.attempts >= config.CODE_MAX_ATTEMPTS:
        raise HTTPException(400, "Too many wrong attempts. Please request a new code.")
    if not hmac.compare_digest(row.code_hash, _hash(user.id, purpose, code.strip())):
        row.attempts += 1
        session.add(row)
        session.commit()
        raise HTTPException(400, "Incorrect code")
    session.delete(row)  # a code can only be used once; the caller commits


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: Session = Depends(get_session)):
    email = data.email.strip().lower()
    user = _get_user(session, email)
    if user and user.is_verified:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user:  # registered earlier but never verified: let them try again
        user.name = data.name.strip()
        user.hashed_password = hash_password(data.password)
    else:
        user = User(
            name=data.name.strip(),
            email=email,
            hashed_password=hash_password(data.password),
            role=Role.CITIZEN,  # never accept a role from the client
            is_verified=not config.REQUIRE_EMAIL_VERIFICATION,
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    if not user.is_verified:
        _issue_code(session, user, "verify")
    return user


@router.post("/verify-email", response_model=Token)
def verify_email(data: VerifyEmailRequest, session: Session = Depends(get_session)):
    user = _get_user(session, data.email)
    if not user:
        raise HTTPException(400, "Incorrect code")
    if user.is_verified:
        raise HTTPException(400, "Email already verified. Please log in.")
    _check_code(session, user, "verify", data.code)
    user.is_verified = True
    session.add(user)
    session.commit()
    return Token(access_token=create_access_token(user))


@router.post("/resend-code")
def resend_code(data: ResendRequest, session: Session = Depends(get_session)):
    user = _get_user(session, data.email)
    if user and not user.is_verified:
        _issue_code(session, user, "verify")
    return {"message": "If this email is waiting for verification, a new code has been sent."}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, session: Session = Depends(get_session)):
    user = _get_user(session, data.email)
    if user:
        _issue_code(session, user, "reset")
    # Same answer whether or not the account exists, so nobody can probe for emails
    return {"message": "If that email has an account, a reset code has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    user = _get_user(session, data.email)
    if not user:
        raise HTTPException(400, "Incorrect code")
    _check_code(session, user, "reset", data.code)
    user.hashed_password = hash_password(data.new_password)
    user.is_verified = True  # they proved they own the email
    session.add(user)
    session.commit()
    return {"message": "Password updated. You can now log in."}


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # OAuth2 form uses the field name "username"; we treat it as the email.
    user = _get_user(session, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if config.REQUIRE_EMAIL_VERIFICATION and not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Enter the code we sent to your email.")
    return Token(access_token=create_access_token(user))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/admin-ping")
def admin_ping(user: User = Depends(require_admin)):
    return {"message": f"Hello admin {user.name}"}