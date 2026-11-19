import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth import hash_password
from app.database import get_session
from app.main import app
from app.models import Role, User
from app import config

@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine):
    def override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_headers(client):
    """Returns a function that registers + logs in a user and gives auth headers."""

    def _make(email="a@test.com"):
        client.post(
            "/auth/register",
            json={"name": "Test User", "email": email, "password": "secret123"},
        )
        token = client.post(
            "/auth/login", data={"username": email, "password": "secret123"}
        ).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make


@pytest.fixture
def admin_headers(client, engine):
    with Session(engine) as session:
        session.add(
            User(
                name="Admin",
                email="admin@test.com",
                hashed_password=hash_password("adminpass"),
                role=Role.ADMIN,
            )
        )
        session.commit()
    token = client.post(
        "/auth/login", data={"username": "admin@test.com", "password": "adminpass"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def no_email_verification(monkeypatch):
    monkeypatch.setattr(config, "REQUIRE_EMAIL_VERIFICATION", False)