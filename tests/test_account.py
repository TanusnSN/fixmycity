import re

import pytest

from app import config
from app.services import mailer


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(mailer, "send_email", lambda to, subject, body: sent.append((to, subject, body)) or True)
    return sent


def code_from(outbox):
    return re.search(r"code is: (\d{6})", outbox[-1][2]).group(1)


def new(client, headers):
    return client.post("/complaints", data={
        "title": "Pothole near bus stop",
        "description": "Large pothole on the main road, dangerous for bikes",
        "category": "ROAD", "lat": "12.2958", "lng": "76.6394",
    }, headers=headers)


def test_email_verification_flow(client, outbox, monkeypatch):
    monkeypatch.setattr(config, "REQUIRE_EMAIL_VERIFICATION", True)
    body = {"name": "Asha", "email": "v@test.com", "password": "secret123"}
    assert client.post("/auth/register", json=body).json()["is_verified"] is False
    login = {"username": "v@test.com", "password": "secret123"}
    assert client.post("/auth/login", data=login).status_code == 403

    code = code_from(outbox)
    wrong = "000000" if code != "000000" else "111111"
    assert client.post("/auth/verify-email", json={"email": "v@test.com", "code": wrong}).status_code == 400
    token = client.post("/auth/verify-email", json={"email": "v@test.com", "code": code}).json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["is_verified"] is True
    assert client.post("/auth/login", data=login).status_code == 200


def test_password_reset(client, outbox):
    client.post("/auth/register", json={"name": "Asha", "email": "r@test.com", "password": "secret123"})
    assert client.post("/auth/forgot-password", json={"email": "r@test.com"}).status_code == 200
    code = code_from(outbox)
    reset = {"email": "r@test.com", "code": code, "new_password": "newpass123"}
    assert client.post("/auth/reset-password", json=reset).status_code == 200
    assert client.post("/auth/login", data={"username": "r@test.com", "password": "newpass123"}).status_code == 200
    assert client.post("/auth/login", data={"username": "r@test.com", "password": "secret123"}).status_code == 401
    assert client.post("/auth/reset-password", json=reset).status_code == 400  # code is single-use


def test_forgot_password_does_not_reveal_unknown_emails(client, outbox):
    assert client.post("/auth/forgot-password", json={"email": "nobody@test.com"}).status_code == 200
    assert outbox == []


def test_edit_only_while_submitted(client, make_headers, admin_headers):
    h = make_headers()
    cid = new(client, h).json()["id"]
    res = client.patch(f"/complaints/{cid}", json={"title": "Pothole on MG Road"}, headers=h)
    assert res.status_code == 200 and res.json()["title"] == "Pothole on MG Road"
    assert client.patch(f"/complaints/{cid}", json={}, headers=h).status_code == 400
    assert client.patch(f"/complaints/{cid}", json={"title": "Hijack attempt"}, headers=make_headers("o@test.com")).status_code == 403
    client.patch(f"/admin/complaints/{cid}", json={"status": "VERIFIED"}, headers=admin_headers)
    assert client.patch(f"/complaints/{cid}", json={"title": "Too late now"}, headers=h).status_code == 400


def test_withdraw(client, make_headers, admin_headers):
    h = make_headers()
    cid = new(client, h).json()["id"]
    assert client.post(f"/complaints/{cid}/withdraw", headers=make_headers("o@test.com")).status_code == 403
    res = client.post(f"/complaints/{cid}/withdraw", headers=h)
    assert res.status_code == 200 and res.json()["status"] == "WITHDRAWN"
    assert client.get("/complaints/public").json() == []
    assert client.get("/admin/stats", headers=admin_headers).json()["open"] == 0
    assert client.patch(f"/admin/complaints/{cid}", json={"status": "VERIFIED"}, headers=admin_headers).status_code == 400


def test_add_admin(client, make_headers, admin_headers):
    h = make_headers("new@test.com")
    assert client.get("/admin/stats", headers=h).status_code == 403
    assert client.post("/admin/admins", json={"email": "nobody@test.com"}, headers=admin_headers).status_code == 404
    assert client.post("/admin/admins", json={"email": "new@test.com"}, headers=admin_headers).status_code == 200
    assert client.get("/admin/stats", headers=h).status_code == 200


def test_purge_resolved(client, make_headers, admin_headers):
    cid = new(client, make_headers()).json()["id"]
    dept = client.post("/admin/departments", json={"name": "Roads"}, headers=admin_headers).json()
    url = f"/admin/complaints/{cid}"
    for body in (
        {"status": "VERIFIED"},
        {"status": "ASSIGNED", "department_id": dept["id"]},
        {"status": "IN_PROGRESS"},
        {"status": "RESOLVED", "remarks": "Fixed"},
    ):
        assert client.patch(url, json=body, headers=admin_headers).status_code == 200
    assert client.delete("/admin/purge?older_than_days=0", headers=admin_headers).json() == {"would_delete": 1, "deleted": 0}
    assert client.delete("/admin/purge?older_than_days=0&confirm=true", headers=admin_headers).json()["deleted"] == 1
    assert client.get(url, headers=admin_headers).status_code == 404