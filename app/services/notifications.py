from sqlmodel import Session, select

from .. import config
from ..models import Notification, Role, User
from .mailer import send_email_async


def notify(session: Session, user_id: int, complaint_id: int | None, message: str, email: bool = True) -> None:
    """Save an in-app notification and (by default) also email the user."""
    session.add(Notification(user_id=user_id, complaint_id=complaint_id, message=message[:300]))
    if email:
        user = session.get(User, user_id)
        if user:
            send_email_async(
                user.email,
                f"FixMyCity update on complaint #{complaint_id}" if complaint_id else "FixMyCity update",
                f"Hello {user.name},\n\n{message}\n\nSee the details: {config.APP_URL}/#/mine/{complaint_id or ''}\n\n- FixMyCity",
            )


def notify_admins(session: Session, complaint_id: int | None, message: str) -> None:
    for admin_id in session.exec(select(User.id).where(User.role == Role.ADMIN)).all():
        notify(session, admin_id, complaint_id, message, email=False)