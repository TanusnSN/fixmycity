from sqlmodel import Session

from app.auth import hash_password
from app.models import Role, User


def register(client, email="a@test.com", password="secret123"):
    return client.post(
        "/auth/register",
        json={"name": "Asha", "email": email, "password": password},
    )


def login(client, email="a@test.com", password="secret123"):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_register_and_login(client):
    assert register(client).status_code == 201
    res = login(client)
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_duplicate_email_rejected(client):
    register(client)
    assert register(client).status_code == 400


def test_wrong_password_rejected(client):
    register(client)
    assert login(client, password="wrongpass").status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_citizen_cannot_access_admin_route(client):
    register(client)
    token = login(client).json()["access_token"]
    res = client.get("/auth/admin-ping", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_admin_can_access_admin_route(client, engine):
    with Session(engine) as session:
        session.add(
            User(
                name="Boss",
                email="boss@test.com",
                hashed_password=hash_password("adminpass"),
                role=Role.ADMIN,
            )
        )
        session.commit()
    token = login(client, "boss@test.com", "adminpass").json()["access_token"]
    res = client.get("/auth/admin-ping", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
