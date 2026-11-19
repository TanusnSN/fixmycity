import os
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, col, select

from .. import config
from ..auth import require_admin
from ..database import get_session
from ..models import (
    AuditLog,
    Complaint,
    ComplaintPhoto,
    Notification,
    Role,
    Status,
    StatusHistory,
    Supporter,
    User,
)

# Every route in this file requires an admin
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


class AdminAdd(BaseModel):
    email: str


def now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/admins")
def list_admins(session: Session = Depends(get_session)):
    rows = session.exec(select(User).where(User.role == Role.ADMIN).order_by(col(User.name))).all()
    return [{"id": u.id, "name": u.name, "email": u.email} for u in rows]


@router.post("/admins")
def add_admin(
    data: AdminAdd,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """Make an existing, registered user an admin. They must register and verify first."""
    user = session.exec(select(User).where(User.email == data.email.strip().lower())).first()
    if not user:
        raise HTTPException(404, "No account with this email. Ask them to register and verify first.")
    if user.role == Role.ADMIN:
        raise HTTPException(400, "This user is already an admin")
    user.role = Role.ADMIN
    session.add(user)
    session.add(AuditLog(user_id=admin.id, action="ADD_ADMIN", entity="user", entity_id=user.id, details=user.email))
    session.commit()
    return {"id": user.id, "name": user.name, "email": user.email}


@router.delete("/purge")
def purge_closed(
    older_than_days: int = Query(30, ge=0, le=3650),
    include: Literal["resolved", "closed"] = "resolved",
    confirm: bool = False,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """Permanently delete old closed complaints with their photos, timeline and notifications.
    Without confirm=true it only reports how many would be deleted."""
    statuses = [Status.RESOLVED] if include == "resolved" else [Status.RESOLVED, Status.REJECTED, Status.WITHDRAWN]
    cutoff = now_naive() - timedelta(days=older_than_days)
    mains = session.exec(
        select(Complaint).where(
            col(Complaint.master_complaint_id).is_(None),
            col(Complaint.status).in_(statuses),
            Complaint.updated_at <= cutoff,
        )
    ).all()
    main_ids = [c.id for c in mains]
    children = (
        session.exec(select(Complaint).where(col(Complaint.master_complaint_id).in_(main_ids))).all()
        if main_ids else []
    )
    ids = main_ids + [c.id for c in children]
    if not confirm or not ids:
        return {"would_delete": len(ids), "deleted": 0}

    for photo in session.exec(select(ComplaintPhoto).where(col(ComplaintPhoto.complaint_id).in_(ids))).all():
        try:
            os.remove(os.path.join(config.UPLOAD_DIR, photo.file_path))
        except OSError:
            pass
        session.delete(photo)
    for model in (StatusHistory, Supporter, Notification):
        for row in session.exec(select(model).where(col(model.complaint_id).in_(ids))).all():
            session.delete(row)
    for child in children:
        child.master_complaint_id = None  # break the links before deleting
        session.add(child)
    session.flush()
    for c in children + mains:
        session.delete(c)
    session.add(AuditLog(
        user_id=admin.id, action="PURGE", entity="complaint",
        details=f"deleted {len(ids)} complaints older than {older_than_days} days ({include})",
    ))
    session.commit()
    return {"would_delete": len(ids), "deleted": len(ids)}