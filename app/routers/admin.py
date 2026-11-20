from datetime import date, datetime, time, timedelta, timezone
from typing import Literal, Optional
from ..services.notifications import notify
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, func, select
import os
from .. import config
from ..auth import require_admin
from ..database import get_session
from ..models import (
    AuditLog,
    Category,
    Complaint,
    ComplaintPhoto,
    Department,
    Notification,
    Priority,
    Role,
    Status,
    StatusHistory,
    Supporter,
    User,
)
from ..schemas import (
    AdminComplaintRead,
    AdminComplaintUpdate,
    DepartmentCreate,
    DepartmentRead,
    MergeRequest,
    SimilarComplaint,
    AdminAdd,
)
from ..services.duplicate import find_similar
from ..services.priority import breakdown_for, recalculate
from .complaints import add_history, count_supporters, get_or_404

# Every route in this file requires an admin
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)

CLOSED = (Status.RESOLVED, Status.REJECTED, Status.WITHDRAWN)

# Which status can follow which. Citizens reopen via their own endpoint.
ALLOWED_TRANSITIONS = {
    Status.SUBMITTED: {Status.VERIFIED, Status.REJECTED},
    Status.VERIFIED: {Status.ASSIGNED, Status.REJECTED},
    Status.ASSIGNED: {Status.IN_PROGRESS, Status.VERIFIED},
    Status.IN_PROGRESS: {Status.RESOLVED, Status.ASSIGNED},
    Status.RESOLVED: set(),
    Status.REJECTED: {Status.VERIFIED},
    Status.REOPENED: {Status.VERIFIED, Status.ASSIGNED, Status.IN_PROGRESS},
    Status.WITHDRAWN: set(),
}


def now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------- helpers ----------

def is_overdue(c: Complaint) -> bool:
    if c.status in CLOSED:
        return False
    days = config.SLA_DAYS.get(Category(c.category).value, 7)
    return now_naive() - c.created_at > timedelta(days=days)


def to_admin_read(session: Session, c: Complaint) -> AdminComplaintRead:
    data = AdminComplaintRead.model_validate(c)
    data.supporters_count = count_supporters(session, c.id)
    citizen = session.get(User, c.citizen_id)
    data.citizen_name = citizen.name if citizen else None
    dept = session.get(Department, c.department_id) if c.department_id else None
    data.department_name = dept.name if dept else None
    data.duplicates_count = session.exec(
        select(func.count())
        .select_from(Complaint)
        .where(Complaint.master_complaint_id == c.id)
    ).one()
    data.is_overdue = is_overdue(c)
    return data


def audit(session: Session, admin: User, action: str, complaint_id: int, details: str):
    session.add(
        AuditLog(
            user_id=admin.id,
            action=action,
            entity="complaint",
            entity_id=complaint_id,
            details=details,
        )
    )


def sync_duplicates(session: Session, master: Complaint, admin_id: int):
    """Copy the main complaint's state onto every duplicate merged into it."""
    children = session.exec(
        select(Complaint).where(Complaint.master_complaint_id == master.id)
    ).all()
    for child in children:
        previous = child.status
        child.status = master.status
        child.priority = master.priority
        child.department_id = master.department_id
        child.resolved_at = master.resolved_at
        child.updated_at = now_naive()
        session.add(child)
        if previous != child.status:
            add_history(
                session, child, previous, child.status,
                f"Updated with main complaint #{master.id}", admin_id,
            )
            notify(
                session, child.citizen_id, child.id,
                f"Your complaint #{child.id} is now {child.status.value.replace('_', ' ').title()} (tracked with #{master.id}).",
            )

# ---------- departments ----------

@router.post("/departments", response_model=DepartmentRead, status_code=201)
def create_department(data: DepartmentCreate, session: Session = Depends(get_session)):
    name = data.name.strip()
    if session.exec(select(Department).where(Department.name == name)).first():
        raise HTTPException(400, "A department with this name already exists")
    dept = Department(name=name, description=data.description)
    session.add(dept)
    session.commit()
    session.refresh(dept)
    return dept


@router.get("/departments", response_model=list[DepartmentRead])
def list_departments(session: Session = Depends(get_session)):
    return session.exec(select(Department).order_by(col(Department.name))).all()


@router.put("/departments/{department_id}", response_model=DepartmentRead)
def update_department(
    department_id: int,
    data: DepartmentCreate,
    session: Session = Depends(get_session),
):
    dept = session.get(Department, department_id)
    if not dept:
        raise HTTPException(404, "Department not found")
    name = data.name.strip()
    clash = session.exec(
        select(Department).where(Department.name == name, Department.id != dept.id)
    ).first()
    if clash:
        raise HTTPException(400, "A department with this name already exists")
    dept.name = name
    dept.description = data.description
    session.add(dept)
    session.commit()
    session.refresh(dept)
    return dept


@router.delete("/departments/{department_id}", status_code=204)
def delete_department(department_id: int, session: Session = Depends(get_session)):
    dept = session.get(Department, department_id)
    if not dept:
        raise HTTPException(404, "Department not found")
    in_use = session.exec(
        select(func.count()).select_from(Complaint).where(Complaint.department_id == dept.id)
    ).one()
    has_staff = session.exec(
        select(func.count()).select_from(User).where(User.department_id == dept.id)
    ).one()
    if in_use or has_staff:
        raise HTTPException(400, "Department is in use and cannot be deleted")
    session.delete(dept)
    session.commit()


# ---------- complaint list ----------

@router.get("/complaints", response_model=list[AdminComplaintRead])
def list_complaints(
    status_filter: Optional[Status] = Query(None, alias="status"),
    category: Optional[Category] = None,
    priority: Optional[Priority] = None,
    department_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    q: Optional[str] = Query(None, max_length=100),
    include_duplicates: bool = False,
    sort: Literal["newest", "score"] = "newest",
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    query = select(Complaint)
    if not include_duplicates:
        query = query.where(col(Complaint.master_complaint_id).is_(None))
    if status_filter:
        query = query.where(Complaint.status == status_filter)
    if category:
        query = query.where(Complaint.category == category)
    if priority:
        query = query.where(Complaint.priority == priority)
    if department_id:
        query = query.where(Complaint.department_id == department_id)
    if date_from:
        query = query.where(Complaint.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.where(Complaint.created_at <= datetime.combine(date_to, time.max))
    if q and q.strip():
        query = query.where(col(Complaint.title).ilike(f"%{q.strip()}%"))

    if sort == "score":
        order = [col(Complaint.priority_score).desc(), col(Complaint.created_at).desc()]
    else:
        order = [col(Complaint.created_at).desc()]

    rows = session.exec(query.order_by(*order).offset(skip).limit(limit)).all()
    return [to_admin_read(session, c) for c in rows]


# ---------- update a complaint ----------

@router.patch("/complaints/{complaint_id}", response_model=AdminComplaintRead)
def update_complaint(
    complaint_id: int,
    data: AdminComplaintUpdate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    c = get_or_404(session, complaint_id)
    if c.master_complaint_id is not None:
        raise HTTPException(
            400,
            f"This is a duplicate of #{c.master_complaint_id}. Update the main complaint instead",
        )

    raw = data.model_dump(exclude_unset=True)
    auto = bool(raw.pop("auto_priority", None))
    changes = {k: v for k, v in raw.items() if v is not None}
    remarks = (changes.pop("remarks", None) or "").strip() or None
    if not changes and not auto:
        raise HTTPException(400, "Nothing to update")

    # Work out which department applies (new one from the request, or the current one)
    dept = None
    if "department_id" in changes:
        dept = session.get(Department, changes["department_id"])
        if not dept:
            raise HTTPException(404, "Department not found")
    elif c.department_id:
        dept = session.get(Department, c.department_id)

    old_status = c.status
    new_status = changes.get("status")
    summary = []

    # Validate the status change before touching anything
    if new_status is not None and new_status != old_status:
        if old_status == Status.WITHDRAWN or new_status == Status.WITHDRAWN:
            raise HTTPException(400, "Withdrawn reports are controlled by the citizen and cannot be changed")
        if new_status == Status.ASSIGNED and dept is None:
            raise HTTPException(400, "Choose a department before assigning")
        if new_status in CLOSED and not remarks:
            raise HTTPException(
                400, f"Remarks are required when marking a complaint {new_status.value.lower()}"
            )

    needs_recalc = auto
    for field in ("category", "priority"):
        if field in changes and changes[field] != getattr(c, field):
            summary.append(f"{field}: {getattr(c, field).value} -> {changes[field].value}")
            setattr(c, field, changes[field])
            if field == "priority":
                c.priority_manual = True  # admin decision beats the automatic score
            else:
                needs_recalc = True

    if "department_id" in changes and dept.id != c.department_id:
        summary.append(f"department: {dept.name}")
        c.department_id = dept.id

    if new_status is not None and new_status != old_status:
        c.status = new_status
        c.resolved_at = now_naive() if new_status == Status.RESOLVED else None
        note = f"Assigned to {dept.name}" if new_status == Status.ASSIGNED else None
        text = " - ".join(x for x in (note, remarks) if x) or None
        add_history(session, c, old_status, new_status, text, admin.id)
        where = f" - assigned to {dept.name}" if new_status == Status.ASSIGNED and dept else ""
        notify(
            session, c.citizen_id, c.id,
            f"Your complaint #{c.id} is now {new_status.value.replace('_', ' ').title()}{where}.",
        )
        summary.append(f"status: {old_status.value} -> {new_status.value}")
    

    if auto:
        c.priority_manual = False
        summary.append("priority: back to automatic")

    if not summary:
        raise HTTPException(400, "No changes made")

    c.updated_at = now_naive()
    session.add(c)
    if needs_recalc:
        recalculate(session, c)
    sync_duplicates(session, c, admin.id)
    audit(session, admin, "UPDATE", c.id, "; ".join(summary))
    session.commit()
    session.refresh(c)
    return to_admin_read(session, c)


# ---------- duplicates: merge / unmerge / list ----------

@router.post("/complaints/{complaint_id}/merge", response_model=AdminComplaintRead)
def merge_complaint(
    complaint_id: int,
    data: MergeRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    c = get_or_404(session, complaint_id)
    if data.master_id == c.id:
        raise HTTPException(400, "A complaint cannot be merged into itself")
    master = get_or_404(session, data.master_id)
    if master.master_complaint_id is not None:
        raise HTTPException(
            400, f"#{master.id} is itself a duplicate. Merge into #{master.master_complaint_id}"
        )

    # Anything already merged into this complaint moves under the new main complaint
    for child in session.exec(
        select(Complaint).where(Complaint.master_complaint_id == c.id)
    ).all():
        child.master_complaint_id = master.id
        session.add(child)

    c.master_complaint_id = master.id
    session.add(c)
    note = f"Merged as duplicate of #{master.id}"
    if data.remarks:
        note += f" - {data.remarks.strip()}"
    add_history(session, c, c.status, c.status, note, admin.id)
    notify(
        session, c.citizen_id, c.id,
        f"Your report #{c.id} was merged with #{master.id}: the same problem was reported nearby. Both are tracked together.",
    )

    session.flush()
    recalculate(session, master)
    sync_duplicates(session, master, admin.id)
    audit(session, admin, "MERGE", c.id, f"merged into #{master.id}")
    session.commit()
    session.refresh(c)
    return to_admin_read(session, c)


@router.post("/complaints/{complaint_id}/unmerge", response_model=AdminComplaintRead)
def unmerge_complaint(
    complaint_id: int,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    c = get_or_404(session, complaint_id)
    if c.master_complaint_id is None:
        raise HTTPException(400, "This complaint is not merged into another one")
    old_master = c.master_complaint_id
    c.master_complaint_id = None
    c.updated_at = now_naive()
    session.add(c)
    add_history(session, c, c.status, c.status, f"Separated from #{old_master}", admin.id)
    session.flush()
    recalculate(session, c)
    previous_master = session.get(Complaint, old_master)
    if previous_master:
        recalculate(session, previous_master)
    audit(session, admin, "UNMERGE", c.id, f"separated from #{old_master}")
    session.commit()
    session.refresh(c)
    return to_admin_read(session, c)


@router.get("/complaints/{complaint_id}/duplicates", response_model=list[AdminComplaintRead])
def list_duplicates(complaint_id: int, session: Session = Depends(get_session)):
    get_or_404(session, complaint_id)
    rows = session.exec(
        select(Complaint)
        .where(Complaint.master_complaint_id == complaint_id)
        .order_by(col(Complaint.created_at))
    ).all()
    return [to_admin_read(session, c) for c in rows]


@router.get("/complaints/{complaint_id}", response_model=AdminComplaintRead)
def admin_get_complaint(complaint_id: int, session: Session = Depends(get_session)):
    return to_admin_read(session, get_or_404(session, complaint_id))


@router.get("/complaints/{complaint_id}/similar", response_model=list[SimilarComplaint])
def similar_complaints(complaint_id: int, session: Session = Depends(get_session)):
    c = get_or_404(session, complaint_id)
    matches = find_similar(
        session, c.category, c.lat, c.lng, c.title, c.description, exclude_id=c.id
    )
    return [
        SimilarComplaint(**m, supporters_count=count_supporters(session, m["id"]))
        for m in matches
    ]


@router.get("/complaints/{complaint_id}/priority")
def priority_breakdown(complaint_id: int, session: Session = Depends(get_session)):
    """Explains exactly how the automatic priority score is made up."""
    return breakdown_for(session, get_or_404(session, complaint_id))


@router.post("/recalculate")
def recalculate_all(
    admin: User = Depends(require_admin), session: Session = Depends(get_session)
):
    """Refresh scores for every open main complaint (the 'days open' part grows over time)."""
    rows = session.exec(
        select(Complaint).where(
            col(Complaint.master_complaint_id).is_(None),
            col(Complaint.status).not_in(CLOSED),
        )
    ).all()
    for c in rows:
        recalculate(session, c)
        sync_duplicates(session, c, admin.id)
    session.commit()
    return {"recalculated": len(rows)}


# ---------- dashboard stats ----------

@router.get("/stats")
def stats(session: Session = Depends(get_session)):
    # Count main complaints only, so merged duplicates don't inflate the numbers
    is_main = col(Complaint.master_complaint_id).is_(None)

    def grouped(column) -> dict:
        rows = session.exec(
            select(column, func.count()).where(is_main).group_by(column)
        ).all()
        return {str(getattr(key, "value", key)): count for key, count in rows}

    total = session.exec(select(func.count()).select_from(Complaint).where(is_main)).one()
    merged = session.exec(
        select(func.count()).select_from(Complaint).where(~is_main)
    ).one()

    by_department = dict(
        session.exec(
            select(Department.name, func.count(Complaint.id))
            .join(Complaint, Complaint.department_id == Department.id)
            .where(is_main)
            .group_by(Department.name)
        ).all()
    )

    open_complaints = session.exec(
        select(Complaint).where(is_main, col(Complaint.status).not_in(CLOSED))
    ).all()
    resolved = session.exec(
        select(func.count()).select_from(Complaint).where(is_main, Complaint.status == Status.RESOLVED)
    ).one()

    return {
        "total": total,
        "open": len(open_complaints),
        "overdue": sum(is_overdue(c) for c in open_complaints),
        "resolved": resolved,
        "resolution_rate": round(resolved / total * 100, 1) if total else 0,
        "merged_duplicates": merged,
        "by_status": grouped(Complaint.status),
        "by_category": grouped(Complaint.category),
        "by_priority": grouped(Complaint.priority),
        "by_department": by_department,
    }
