"""Demo data: python -m app.seed

Creates departments, an admin, three citizens and ~20 complaints around Mysuru,
including deliberate duplicates so the duplicate detection is easy to demo.
"""
from datetime import timedelta

from sqlmodel import Session, select

from .auth import hash_password
from .database import engine, init_db
from .models import (
    Category, Complaint, Department, Priority, Role, Status,
    StatusHistory, Supporter, User, utcnow,
)
from .services.priority import recalculate
from .create_admin import DEFAULT_DEPARTMENTS

LAT, LNG = 12.2958, 76.6394
DEPT_FOR = {
    "ROAD": "Roads & Highways", "STREETLIGHT": "Electricity",
    "WATER_LEAKAGE": "Water Supply", "DRAINAGE": "Sanitation & Drainage", "OTHER": "Roads & Highways",
}
CHAIN = ["SUBMITTED", "VERIFIED", "ASSIGNED", "IN_PROGRESS", "RESOLVED"]

# (title, description, category, dlat, dlng, status, citizen, days_ago, dup_of_index_or_None)
DATA = [
    ("Deep pothole near bus stop", "Large pothole on the main road, dangerous for bikes", "ROAD", 0.0000, 0.0000, "IN_PROGRESS", 0, 6, None),
    ("Pothole at bus stop", "Big pothole on the main road near the bus stop, two-wheelers skid", "ROAD", 0.0001, 0.0001, "IN_PROGRESS", 1, 5, 0),
    ("Road damaged near bus stop", "Large pothole on main road, very dangerous for bikes at night", "ROAD", -0.0001, 0.0002, "IN_PROGRESS", 2, 3, 0),
    ("Streetlight not working", "Streetlight outside the primary school has been off for a week", "STREETLIGHT", 0.0040, 0.0030, "ASSIGNED", 0, 8, None),
    ("Street light off near school", "The light near the school gate is not working, kids walk in the dark", "STREETLIGHT", 0.0041, 0.0031, "ASSIGNED", 1, 4, 3),
    ("Water pipe leaking", "Drinking water pipe is leaking and wasting water on the road", "WATER_LEAKAGE", -0.0050, 0.0060, "VERIFIED", 2, 3, None),
    ("Burst pipe near hospital", "Water pipe burst near the hospital entrance, road is flooded", "WATER_LEAKAGE", 0.0070, -0.0040, "SUBMITTED", 1, 1, None),
    ("Drain overflowing", "Drainage is overflowing onto the street, very bad smell", "DRAINAGE", -0.0080, -0.0050, "SUBMITTED", 0, 2, None),
    ("Overflowing drain in market", "Sewage drain overflowing in the market lane, shops affected", "DRAINAGE", -0.0081, -0.0049, "SUBMITTED", 2, 1, 7),
    ("Blocked drain after rain", "Drain blocked with plastic, water stands on the road after rain", "DRAINAGE", 0.0100, 0.0090, "RESOLVED", 1, 12, None),
    ("Broken road near junction", "Road surface broken and uneven near the junction", "ROAD", 0.0120, -0.0100, "VERIFIED", 0, 4, None),
    ("Flickering streetlight", "Streetlight flickers all night on the park road", "STREETLIGHT", -0.0110, 0.0110, "SUBMITTED", 2, 2, None),
    ("Leaking tap at public stand", "Public water tap is leaking continuously", "WATER_LEAKAGE", 0.0150, 0.0020, "RESOLVED", 0, 15, None),
    ("Garbage on the road", "Garbage pile is blocking half of the road", "OTHER", -0.0140, -0.0130, "REJECTED", 1, 9, None),
    ("Pothole outside college gate", "Deep pothole right outside the college gate, students fall regularly", "ROAD", 0.0180, 0.0150, "SUBMITTED", 2, 1, None),
]


def main():
    init_db()
    with Session(engine) as s:
        if s.exec(select(Complaint)).first():
            print("Database already has complaints. Delete fixmycity.db to reseed.")
            return

        depts = {}
        for name, desc in DEFAULT_DEPARTMENTS:
            d = s.exec(select(Department).where(Department.name == name)).first()
            if not d:
                d = Department(name=name, description=desc)
                s.add(d)
                s.flush()
            depts[name] = d

        def user(name, email, pw, role=Role.CITIZEN):
            u = s.exec(select(User).where(User.email == email)).first()
            if not u:
                u = User(name=name, email=email, hashed_password=hash_password(pw), role=role)
                s.add(u)
                s.flush()
            return u

        admin = user("Admin", "admin@fixmycity.local", "admin123", Role.ADMIN)
        citizens = [
            user("Asha Rao", "citizen@fixmycity.local", "citizen123"),
            user("Ravi Kumar", "ravi@fixmycity.local", "citizen123"),
            user("Meena Iyer", "meena@fixmycity.local", "citizen123"),
        ]

        made: list[Complaint] = []
        for title, desc, cat, dlat, dlng, status, who, days, dup_of in DATA:
            created = utcnow() - timedelta(days=days)
            c = Complaint(
                title=title, description=desc, category=Category(cat),
                lat=LAT + dlat, lng=LNG + dlng, citizen_id=citizens[who].id,
                created_at=created, updated_at=created,
            )
            s.add(c)
            s.flush()
            made.append(c)

            path = ["SUBMITTED", "REJECTED"] if status == "REJECTED" else CHAIN[: CHAIN.index(status) + 1] if status in CHAIN else ["SUBMITTED"]
            prev = None
            for i, st in enumerate(path):
                s.add(StatusHistory(
                    complaint_id=c.id, old_status=Status(prev) if prev else None, new_status=Status(st),
                    remarks="Complaint submitted" if st == "SUBMITTED" else (
                        "Not a municipal issue" if st == "REJECTED" else f"Moved to {st.lower().replace('_', ' ')}"),
                    changed_by=admin.id if prev else citizens[who].id,
                    changed_at=created + timedelta(hours=6 * i),
                ))
                prev = st
            c.status = Status(status)
            if status in ("ASSIGNED", "IN_PROGRESS", "RESOLVED"):
                c.department_id = depts[DEPT_FOR[cat]].id
            if status == "RESOLVED":
                c.resolved_at = created + timedelta(days=min(days, 3))
            s.add(c)

        # supporters on a few main complaints
        for idx, supporters in {0: [1, 2], 3: [1], 5: [0, 1], 7: [1]}.items():
            for u in supporters:
                if citizens[u].id != made[idx].citizen_id:
                    s.add(Supporter(complaint_id=made[idx].id, user_id=citizens[u].id))
        s.flush()

        # merge duplicates under their main complaint
        for i, row in enumerate(DATA):
            if row[8] is not None:
                made[i].master_complaint_id = made[row[8]].id
                made[i].status = made[row[8]].status
                s.add(made[i])
        s.flush()

        for i, row in enumerate(DATA):
            if row[8] is None:
                recalculate(s, made[i])
        s.flush()
        for i, row in enumerate(DATA):
            if row[8] is not None:
                m = made[row[8]]
                made[i].priority, made[i].priority_score = m.priority, m.priority_score
                s.add(made[i])
        s.commit()
        print(f"Seeded {len(DATA)} complaints.")
        print("Admin:   admin@fixmycity.local / admin123")
        print("Citizen: citizen@fixmycity.local / citizen123")


if __name__ == "__main__":
    main()
