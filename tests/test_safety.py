from app import config


def new(client, headers):
    return client.post("/complaints", data={
        "title": "Pothole near bus stop",
        "description": "Large pothole on the main road, dangerous for bikes",
        "category": "ROAD", "lat": "12.2958", "lng": "76.6394",
    }, headers=headers)


def test_block_and_unblock(client, make_headers, admin_headers):
    h = make_headers("bad@test.com")
    uid = client.get("/auth/me", headers=h).json()["id"]
    assert client.post(f"/admin/users/{uid}/block", json={"reason": "Fake reports"}, headers=admin_headers).status_code == 200
    assert client.get("/auth/me", headers=h).status_code == 401
    assert client.post("/auth/login", data={"username": "bad@test.com", "password": "secret123"}).status_code == 423
    assert client.post(f"/admin/users/{uid}/unblock", headers=admin_headers).status_code == 200
    assert client.get("/auth/me", headers=h).status_code == 200


def test_cannot_block_admin(client, admin_headers):
    admin_id = client.get("/auth/me", headers=admin_headers).json()["id"]
    assert client.post(f"/admin/users/{admin_id}/block", json={}, headers=admin_headers).status_code == 400


def test_daily_report_limit(client, make_headers, monkeypatch):
    monkeypatch.setattr(config, "MAX_REPORTS_PER_DAY", 2)
    h = make_headers()
    assert new(client, h).status_code == 201
    assert new(client, h).status_code == 201
    assert new(client, h).status_code == 429


def test_login_with_phone(client):
    body = {"name": "Asha", "email": "p@test.com", "password": "secret123", "phone": "98765 43210"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/login", data={"username": "9876543210", "password": "secret123"}).status_code == 200
    again = {"name": "Other", "email": "q@test.com", "password": "secret123", "phone": "+91 98765-43210"}
    assert client.post("/auth/register", json=again).status_code == 400


def test_admin_can_set_any_status(client, make_headers, admin_headers):
    cid = new(client, make_headers()).json()["id"]
    res = client.patch(f"/admin/complaints/{cid}", json={"status": "RESOLVED", "remarks": "Fixed on site"}, headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "RESOLVED"