import pytest
from sqlmodel import Session

from app import config
from app.models import Complaint, Status

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


@pytest.fixture(autouse=True)
def tmp_uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOAD_DIR", str(tmp_path))


def create(client, headers, files=None, **overrides):
    data = {
        "title": "Pothole near bus stop",
        "description": "Large pothole on the main road, dangerous for bikes",
        "category": "ROAD",
        "lat": "12.2958",
        "lng": "76.6394",
    }
    data.update(overrides)
    return client.post("/complaints", data=data, files=files, headers=headers)


def test_create_complaint_without_photo(client, make_headers):
    res = create(client, make_headers())
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "SUBMITTED"
    assert len(body["timeline"]) == 1
    assert body["photos"] == []


def test_create_complaint_with_photo(client, make_headers):
    files = [("photos", ("p.png", PNG, "image/png"))]
    res = create(client, make_headers(), files=files)
    assert res.status_code == 201
    assert len(res.json()["photos"]) == 1


def test_rejects_non_image_upload(client, make_headers):
    files = [("photos", ("notes.txt", b"hello", "text/plain"))]
    assert create(client, make_headers(), files=files).status_code == 400


def test_rejects_fake_image(client, make_headers):
    files = [("photos", ("fake.png", b"not really a png", "image/png"))]
    assert create(client, make_headers(), files=files).status_code == 400


def test_rejects_invalid_coordinates(client, make_headers):
    assert create(client, make_headers(), lat="123").status_code == 422


def test_requires_login(client):
    assert create(client, headers={}).status_code == 401


def test_mine_only_returns_own(client, make_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    create(client, a)
    create(client, b)
    mine = client.get("/complaints/mine", headers=a).json()
    assert len(mine) == 1


def test_other_user_cannot_view_detail(client, make_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    cid = create(client, a).json()["id"]
    assert client.get(f"/complaints/{cid}", headers=a).status_code == 200
    assert client.get(f"/complaints/{cid}", headers=b).status_code == 403


def test_support_rules(client, make_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    cid = create(client, a).json()["id"]
    assert client.post(f"/complaints/{cid}/support", headers=a).status_code == 400
    res = client.post(f"/complaints/{cid}/support", headers=b)
    assert res.status_code == 200
    assert res.json()["supporters_count"] == 1
    assert client.post(f"/complaints/{cid}/support", headers=b).status_code == 400


def test_reopen_flow(client, engine, make_headers):
    a = make_headers()
    cid = create(client, a).json()["id"]
    body = {"reason": "The pothole is back again"}

    # not resolved yet
    assert client.post(f"/complaints/{cid}/reopen", json=body, headers=a).status_code == 400

    with Session(engine) as s:
        c = s.get(Complaint, cid)
        c.status = Status.RESOLVED
        s.add(c)
        s.commit()

    res = client.post(f"/complaints/{cid}/reopen", json=body, headers=a)
    assert res.status_code == 200
    assert res.json()["status"] == "REOPENED"
    assert res.json()["timeline"][-1]["remarks"] == "The pothole is back again"


def test_public_list_hides_personal_info(client, make_headers):
    create(client, make_headers())
    res = client.get("/complaints/public")
    assert res.status_code == 200
    item = res.json()[0]
    assert "citizen_id" not in item
    assert "description" not in item
