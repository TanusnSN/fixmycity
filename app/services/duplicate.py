"""Duplicate-complaint detection.

A new complaint is compared with open complaints of the SAME category that are
within RADIUS_M metres. The confidence score blends two signals:

    confidence = 0.6 * proximity + 0.4 * text_similarity

    proximity       = 1 - distance / RADIUS_M     (1.0 = same spot, 0.0 = at the edge)
    text_similarity = 0.5 * word overlap (Jaccard) + 0.5 * character similarity

>= 0.75 -> LIKELY duplicate, 0.50 - 0.75 -> POSSIBLE duplicate (admin should review).
"""
import difflib
import math
import re

from sqlmodel import Session, col, select

from ..models import Complaint, Status

RADIUS_M = 100.0
W_DISTANCE = 0.6
W_TEXT = 0.4
LIKELY = 0.75
POSSIBLE = 0.50
CLOSED = (Status.RESOLVED, Status.REJECTED)

STOPWORDS = {
    "the", "and", "for", "are", "was", "has", "have", "with", "near", "this", "that",
    "from", "very", "there", "been", "not", "but", "its", "our", "out", "all", "can",
}


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in metres."""
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def text_similarity(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    jaccard = len(ta & tb) / len(ta | tb) if ta and tb else 0.0
    ratio = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return round(0.5 * jaccard + 0.5 * ratio, 3)


def find_similar(
    session: Session,
    category,
    lat: float,
    lng: float,
    title: str,
    description: str,
    exclude_id: int | None = None,
    limit: int = 5,
) -> list[dict]:
    # Cheap pre-filter: a bounding box around the point (index friendly)
    dlat = RADIUS_M / 111_320
    dlng = RADIUS_M / (111_320 * max(math.cos(math.radians(lat)), 0.01))

    query = select(Complaint).where(
        Complaint.category == category,
        col(Complaint.master_complaint_id).is_(None),
        col(Complaint.status).not_in(CLOSED),
        col(Complaint.lat).between(lat - dlat, lat + dlat),
        col(Complaint.lng).between(lng - dlng, lng + dlng),
    )
    if exclude_id is not None:
        query = query.where(Complaint.id != exclude_id)

    new_text = f"{title} {description}"
    results = []
    for c in session.exec(query).all():
        distance = haversine_m(lat, lng, c.lat, c.lng)
        if distance > RADIUS_M:
            continue
        proximity = 1 - distance / RADIUS_M
        sim = text_similarity(new_text, f"{c.title} {c.description}")
        confidence = round(W_DISTANCE * proximity + W_TEXT * sim, 3)
        if confidence < POSSIBLE:
            continue
        results.append(
            {
                "id": c.id,
                "title": c.title,
                "status": c.status,
                "distance_m": round(distance, 1),
                "text_similarity": sim,
                "confidence": confidence,
                "level": "LIKELY" if confidence >= LIKELY else "POSSIBLE",
            }
        )
    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results[:limit]
