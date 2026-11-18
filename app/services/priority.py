"""Transparent priority scoring. Every point is explained in the breakdown.

score = base(category) + 4 per duplicate report (max 10) + 2 per supporter (max 10)
        + 1.5 per day open (max 10 days) + 15 if near a sensitive place

LOW < 30 <= MEDIUM < 50 <= HIGH < 70 <= CRITICAL
Admins can override the priority manually; the score keeps updating regardless.
"""
from datetime import datetime, timezone

from sqlmodel import Session, func, select

from ..models import Complaint, Priority, Supporter

BASE_POINTS = {
    "WATER_LEAKAGE": 30,
    "DRAINAGE": 30,
    "ROAD": 25,
    "STREETLIGHT": 20,
    "OTHER": 10,
}
SENSITIVE_WORDS = (
    "school", "hospital", "clinic", "college", "highway",
    "junction", "crossing", "market", "station",
)


def band(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def breakdown(category, title, description, address, duplicates, supporters, created_at, now=None):
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    cat = getattr(category, "value", category)
    days = max((now - created_at).total_seconds() / 86400, 0)
    text = f"{title} {description} {address or ''}".lower()
    found = [w for w in SENSITIVE_WORDS if w in text]

    parts = [
        {"label": "Category base", "points": BASE_POINTS.get(cat, 10), "detail": cat},
        {"label": "Duplicate reports", "points": 4 * min(duplicates, 10), "detail": f"{duplicates} merged"},
        {"label": "Citizen supporters", "points": 2 * min(supporters, 10), "detail": f"{supporters} supporters"},
        {"label": "Days open", "points": round(1.5 * min(days, 10), 1), "detail": f"{days:.1f} days"},
        {"label": "Sensitive location", "points": 15 if found else 0, "detail": ", ".join(found) or "none"},
    ]
    score = round(sum(p["points"] for p in parts), 1)
    return {"components": parts, "score": score, "priority": band(score)}


def breakdown_for(session: Session, c: Complaint) -> dict:
    duplicates = session.exec(
        select(func.count()).select_from(Complaint).where(Complaint.master_complaint_id == c.id)
    ).one()
    supporters = session.exec(
        select(func.count()).select_from(Supporter).where(Supporter.complaint_id == c.id)
    ).one()
    return breakdown(
        c.category, c.title, c.description, c.address, duplicates, supporters, c.created_at
    )


def recalculate(session: Session, c: Complaint) -> dict:
    """Update the stored score; update the priority too unless an admin set it manually."""
    session.flush()
    info = breakdown_for(session, c)
    c.priority_score = info["score"]
    if not c.priority_manual:
        c.priority = Priority(info["priority"])
    session.add(c)
    return info
