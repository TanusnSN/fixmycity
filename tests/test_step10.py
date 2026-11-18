from datetime import datetime, timedelta

from app.services.duplicate import haversine_m, text_similarity
from app.services.priority import band, breakdown

LAT, LNG = 12.2958, 76.6394


def new(client, headers, **o):
    data = {
        "title": "Pothole near bus stop",
        "description": "Large pothole on the main road, dangerous for bikes",
        "category": "ROAD",
        "lat": str(LAT),
        "lng": str(LNG),
    }
    data.update(o)
    return client.post("/complaints", data=data, headers=headers)


def check(client, headers, **o):
    body = {
        "category": "ROAD",
        "lat": LAT,
        "lng": LNG,
        "title": "Pothole near bus stop",
        "description": "Large pothole on the main road, dangerous for bikes",
    }
    body.update(o)
    return client.post("/complaints/check-duplicate", json=body, headers=headers)


# ---------- pure functions ----------

def test_haversine():
    assert haversine_m(LAT, LNG, LAT, LNG) == 0
    assert 90 < haversine_m(LAT, LNG, LAT, LNG + 0.0009) < 110


def test_text_similarity():
    same = text_similarity("Large pothole on main road", "Large pothole on main road")
    other = text_similarity("Large pothole on main road", "Streetlight bulb fused since monday")
    assert same > 0.95
    assert other < 0.35


def test_priority_bands():
    assert band(10) == "LOW" and band(30) == "MEDIUM"
    assert band(50) == "HIGH" and band(70) == "CRITICAL"


def test_priority_breakdown_components():
    now = datetime(2026, 1, 10)
    plain = breakdown("ROAD", "Pothole", "on the road", None, 0, 0, now, now=now)
    assert plain["score"] == 25 and plain["priority"] == "LOW"

    risky = breakdown(
        "WATER_LEAKAGE", "Leak", "pipe burst near the hospital gate", None,
        3, 2, now - timedelta(days=4), now=now,
    )
    # 30 base + 12 duplicates + 4 supporters + 6 days + 15 sensitive = 67
    assert risky["score"] == 67 and risky["priority"] == "HIGH"
    assert [p["label"] for p in risky["components"]][0] == "Category base"


# ---------- duplicate detection through the API ----------

def test_check_duplicate_requires_login(client):
    assert client.post("/complaints/check-duplicate", json={}).status_code == 401


def test_likely_duplicate_same_spot(client, make_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    cid = new(client, a).json()["id"]
    res = check(client, b)
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) == 1
    assert matches[0]["id"] == cid
    assert matches[0]["level"] == "LIKELY"
    assert matches[0]["distance_m"] == 0


def test_possible_duplicate_60m_away(client, make_headers):
    a = make_headers()
    new(client, a)
    matches = check(client, a, lng=LNG + 0.00055).json()
    assert len(matches) == 1 and matches[0]["level"] == "POSSIBLE"


def test_no_match_far_away_or_other_category(client, make_headers):
    a = make_headers()
    new(client, a)
    assert check(client, a, lat=LAT + 0.01).json() == []
    assert check(client, a, category="DRAINAGE").json() == []


def test_closed_complaints_are_ignored(client, make_headers, admin_headers):
    a = make_headers()
    cid = new(client, a).json()["id"]
    client.patch(f"/admin/complaints/{cid}", json={"status": "REJECTED", "remarks": "spam"}, headers=admin_headers)
    assert check(client, a).json() == []


def test_admin_similar_endpoint(client, make_headers, admin_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    first = new(client, a).json()["id"]
    second = new(client, b).json()["id"]
    res = client.get(f"/admin/complaints/{second}/similar", headers=admin_headers)
    assert [m["id"] for m in res.json()] == [first]


# ---------- automatic priority ----------

def test_priority_is_automatic_on_create(client, make_headers):
    body = new(client, make_headers(), category="DRAINAGE",
               description="Drain overflowing right outside the primary school").json()
    assert body["priority"] == "MEDIUM"  # 30 base + 15 sensitive location


def test_merge_raises_master_score(client, make_headers, admin_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    id1 = new(client, a).json()["id"]
    id2 = new(client, b).json()["id"]
    before = client.get(f"/admin/complaints/{id1}", headers=admin_headers).json()["priority_score"]
    client.post(f"/admin/complaints/{id2}/merge", json={"master_id": id1}, headers=admin_headers)
    after = client.get(f"/admin/complaints/{id1}", headers=admin_headers).json()["priority_score"]
    assert after > before

    info = client.get(f"/admin/complaints/{id1}/priority", headers=admin_headers).json()
    dup = [p for p in info["components"] if p["label"] == "Duplicate reports"][0]
    assert dup["points"] == 4


def test_manual_priority_survives_new_supporters(client, make_headers, admin_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    cid = new(client, a).json()["id"]
    url = f"/admin/complaints/{cid}"
    client.patch(url, json={"priority": "CRITICAL"}, headers=admin_headers)
    client.post(f"/complaints/{cid}/support", headers=b)

    c = client.get(url, headers=admin_headers).json()
    assert c["priority"] == "CRITICAL" and c["priority_manual"] is True
    assert c["priority_score"] == 27  # 25 base + 2 for the supporter

    back = client.patch(url, json={"auto_priority": True}, headers=admin_headers).json()
    assert back["priority_manual"] is False and back["priority"] == "LOW"


def test_recalculate_all(client, make_headers, admin_headers):
    new(client, make_headers())
    res = client.post("/admin/recalculate", headers=admin_headers)
    assert res.status_code == 200 and res.json()["recalculated"] == 1


def test_frontend_is_served(client):
    res = client.get("/")
    assert res.status_code == 200 and "FixMyCity" in res.text
