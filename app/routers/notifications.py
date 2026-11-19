from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, func, select
from ..services.notifications import notify, notify_admins
from ..auth import get_current_user
from ..database import get_session
from ..models import Notification, User
from ..schemas import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    limit: int = Query(30, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return session.exec(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(col(Notification.created_at).desc(), col(Notification.id).desc())
        .limit(limit)
    ).all()


@router.get("/unread-count")
def unread_count(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    count = session.exec(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.id, Notification.is_read == False)  # noqa: E712
    ).one()
    return {"unread": count}


@router.post("/read-all")
def mark_all_read(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    rows = session.exec(
        select(Notification).where(Notification.user_id == user.id, Notification.is_read == False)  # noqa: E712
    ).all()
    for n in rows:
        n.is_read = True
        session.add(n)
    session.commit()
    return {"marked": len(rows)}


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    n = session.get(Notification, notification_id)
    if not n or n.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    session.add(n)
    session.commit()
    session.refresh(n)
    return n