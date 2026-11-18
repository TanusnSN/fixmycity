import os
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlmodel import Session, col, func, select

from .. import config
from ..auth import get_current_user
from ..database import get_session
from ..models import (
    Category,
    Complaint,
    ComplaintPhoto,
    Role,
    Status,
    StatusHistory,
    Supporter,
    User,
)
from ..services.duplicate import find_similar
from ..services.priority import recalculate
from ..schemas import (
    ComplaintDetail,
    ComplaintRead,
    DuplicateCheckRequest,
    PhotoRead,
    PublicComplaint,
    ReopenRequest,
    SimilarComplaint,
    StatusHistoryRead,
)

router = APIRouter(prefix="/complaints", tags=["complaints"])

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------- helpers ----------

def looks_like_image(content_type: str, data: bytes) -> bool:
    """Check the real file signature, not just the declared type."""
    if content_type == "image/jpeg":
        return data[:3] == b"\xff\xd8\xff"
    if content_type == "image/png":
        return data[:8] == b"\x89PNG\r\n\x1a\n"
    if content_type == "image/webp":
        return data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return False


async def validate_photo(file: UploadFile) -> tuple[bytes, str]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Only JPEG, PNG or WebP images are allowed")
    data = await file.read(config.MAX_PHOTO_BYTES + 1)
    if len(data) > config.MAX_PHOTO_BYTES:
        raise HTTPException(400, "Each photo must be 5 MB or smaller")
    if not looks_like_image(file.content_type, data):
        raise HTTPException(400, "File content does not match an image type")
    return data, ALLOWED_TYPES[file.content_type]


def save_photo_file(data: bytes, ext: str) -> str:
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    name = f"{uuid4().hex}{ext}"
    with open(os.path.join(config.UPLOAD_DIR, name), "wb") as f:
        f.write(data)
    return name


def add_history(session, complaint, old, new, remarks, user_id):
    session.add(
        StatusHistory(
            complaint_id=complaint.id,
            old_status=old,
            new_status=new,
            remarks=remarks,
            changed_by=user_id,
        )
    )


def count_supporters(session: Session, complaint_id: int) -> int:
    return session.exec(
        select(func.count())
        .select_from(Supporter)
        .where(Supporter.complaint_id == complaint_id)
    ).one()


def get_or_404(session: Session, complaint_id: int) -> Complaint:
    complaint = session.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    return complaint


def to_read(session: Session, c: Complaint) -> ComplaintRead:
    data = ComplaintRead.model_validate(c)
    data.supporters_count = count_supporters(session, c.id)
    return data


def to_detail(session: Session, c: Complaint) -> ComplaintDetail:
    base = to_read(session, c)
    photos = session.exec(
        select(ComplaintPhoto).where(ComplaintPhoto.complaint_id == c.id)
    ).all()
    timeline = session.exec(
        select(StatusHistory)
        .where(StatusHistory.complaint_id == c.id)
        .order_by(col(StatusHistory.changed_at), col(StatusHistory.id))
    ).all()
    return ComplaintDetail(
        **base.model_dump(),
        photos=[PhotoRead(id=p.id, url=f"/uploads/{p.file_path}") for p in photos],
        timeline=[StatusHistoryRead.model_validate(h) for h in timeline],
    )


# ---------- endpoints ----------
# NOTE: /mine and /public must be defined BEFORE /{complaint_id},
# otherwise FastAPI tries to read "mine" as an integer id.

@router.post("", response_model=ComplaintDetail, status_code=201)
async def create_complaint(
    title: str = Form(..., min_length=5, max_length=120),
    description: str = Form(..., min_length=10, max_length=2000),
    category: Category = Form(...),
    lat: float = Form(..., ge=-90, le=90),
    lng: float = Form(..., ge=-180, le=180),
    address: Optional[str] = Form(None, max_length=255),
    photos: Optional[list[UploadFile]] = File(None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    files = [p for p in (photos or []) if p.filename]
    if len(files) > config.MAX_PHOTOS:
        raise HTTPException(400, f"You can upload at most {config.MAX_PHOTOS} photos")

    # Validate everything first so a bad file doesn't leave a half-created complaint
    validated = [await validate_photo(p) for p in files]

    complaint = Complaint(
        title=title.strip(),
        description=description.strip(),
        category=category,
        lat=lat,
        lng=lng,
        address=address.strip() if address else None,
        citizen_id=user.id,
    )
    session.add(complaint)
    session.flush()  # gives the complaint an id without committing yet

    add_history(session, complaint, None, Status.SUBMITTED, "Complaint submitted", user.id)
    for data, ext in validated:
        name = save_photo_file(data, ext)
        session.add(ComplaintPhoto(complaint_id=complaint.id, file_path=name))

    recalculate(session, complaint)
    session.commit()
    session.refresh(complaint)
    return to_detail(session, complaint)


@router.get("/mine", response_model=list[ComplaintRead])
def my_complaints(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(
        select(Complaint)
        .where(Complaint.citizen_id == user.id)
        .order_by(col(Complaint.created_at).desc())
    ).all()
    return [to_read(session, c) for c in rows]


@router.get("/public", response_model=list[PublicComplaint])
def public_complaints(
    status_filter: Optional[Status] = Query(None, alias="status"),
    category: Optional[Category] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    query = select(Complaint).where(
        col(Complaint.master_complaint_id).is_(None),  # hide merged duplicates
        Complaint.status != Status.REJECTED,
    )
    if status_filter:
        query = query.where(Complaint.status == status_filter)
    if category:
        query = query.where(Complaint.category == category)
    rows = session.exec(
        query.order_by(col(Complaint.created_at).desc()).offset(skip).limit(limit)
    ).all()
    return [
        PublicComplaint(
            id=c.id,
            title=c.title,
            category=c.category,
            lat=c.lat,
            lng=c.lng,
            status=c.status,
            priority=c.priority,
            created_at=c.created_at,
            supporters_count=count_supporters(session, c.id),
        )
        for c in rows
    ]


@router.post("/check-duplicate", response_model=list[SimilarComplaint])
def check_duplicate(
    data: DuplicateCheckRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    matches = find_similar(
        session, data.category, data.lat, data.lng, data.title, data.description
    )
    return [
        SimilarComplaint(**m, supporters_count=count_supporters(session, m["id"]))
        for m in matches
    ]


@router.get("/{complaint_id}", response_model=ComplaintDetail)
def complaint_detail(
    complaint_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    complaint = get_or_404(session, complaint_id)
    if complaint.citizen_id != user.id and user.role != Role.ADMIN:
        raise HTTPException(403, "You can only view your own complaints")
    return to_detail(session, complaint)


@router.post("/{complaint_id}/support", response_model=ComplaintRead)
def support_complaint(
    complaint_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    complaint = get_or_404(session, complaint_id)
    if complaint.citizen_id == user.id:
        raise HTTPException(400, "You reported this complaint yourself")
    if complaint.status in (Status.RESOLVED, Status.REJECTED):
        raise HTTPException(400, "This complaint is already closed")
    already = session.exec(
        select(Supporter).where(
            Supporter.complaint_id == complaint_id, Supporter.user_id == user.id
        )
    ).first()
    if already:
        raise HTTPException(400, "You already supported this complaint")

    session.add(Supporter(complaint_id=complaint_id, user_id=user.id))
    session.flush()
    recalculate(session, complaint)
    session.commit()
    return to_read(session, complaint)


@router.post("/{complaint_id}/reopen", response_model=ComplaintDetail)
def reopen_complaint(
    complaint_id: int,
    data: ReopenRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    complaint = get_or_404(session, complaint_id)
    if complaint.citizen_id != user.id:
        raise HTTPException(403, "Only the person who reported it can reopen it")
    if complaint.status != Status.RESOLVED:
        raise HTTPException(400, "Only resolved complaints can be reopened")

    old = complaint.status
    complaint.status = Status.REOPENED
    complaint.resolved_at = None
    complaint.updated_at = now_naive()
    session.add(complaint)
    add_history(session, complaint, old, Status.REOPENED, data.reason, user.id)
    session.commit()
    session.refresh(complaint)
    return to_detail(session, complaint)
