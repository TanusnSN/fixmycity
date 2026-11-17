import os

from sqlmodel import Session, select

from .auth import hash_password
from .database import engine, init_db
from .models import Role, User


def main():
    init_db()
    email = os.getenv("ADMIN_EMAIL", "admin@fixmycity.local")
    password = os.getenv("ADMIN_PASSWORD", "admin123")

    with Session(engine) as session:
        if session.exec(select(User).where(User.email == email)).first():
            print("Admin already exists")
            return
        session.add(
            User(
                name="Admin",
                email=email,
                hashed_password=hash_password(password),
                role=Role.ADMIN,
            )
        )
        session.commit()
        print(f"Admin created: {email}")


if __name__ == "__main__":
    main()