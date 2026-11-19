import os

from sqlmodel import Session, select

from .auth import hash_password
from .database import engine, init_db
from .models import Department, Role, User

DEFAULT_DEPARTMENTS = [
    ("Roads & Highways", "Potholes and damaged roads"),
    ("Electricity", "Streetlights and power lines"),
    ("Water Supply", "Leakages and supply problems"),
    ("Sanitation & Drainage", "Overflowing drains and sewage"),
]


def main():
    init_db()
    email = os.getenv("ADMIN_EMAIL", "admin@fixmycity.local")
    password = os.getenv("ADMIN_PASSWORD", "admin123")

    with Session(engine) as session:
        for name, description in DEFAULT_DEPARTMENTS:
            if not session.exec(select(Department).where(Department.name == name)).first():
                session.add(Department(name=name, description=description))

        existing_admin = session.exec(select(User).where(User.email == email)).first()
        if existing_admin:
            existing_admin.is_verified = True
            session.add(existing_admin)
            print("Admin already exists (ensured is_verified=True)")
        else:
            session.add(
                User(
                    name="Admin",
                    email=email,
                    hashed_password=hash_password(password),
                    role=Role.ADMIN,
                    is_verified=True,
                )
            )
            print(f"Admin created: {email}")
        session.commit()


if __name__ == "__main__":
    main()