import pytest


def new(client, headers, **overrides):
    data = {
        "title": "Pothole near bus stop",
        "description": "Large pothole on the main road, dangerous for bikes",
        "category": "ROAD",
        "lat": "12.2958",
        "lng": "76.6394",
    }
    data.update(overrides)
    return client.post("/complaints", data=data, headers=headers)


@pytest.mark.parametrize("path", ["/admin/stats", "/admin/complaints", "/admin/departments"])
def test_admin_routes_are_protected(client, make_headers, path):
    assert client.get(path).status_code == 401
    assert client.get(path, headers=make_headers()).status_code == 403


def test_department_rules(client, make_headers, admin_headers):
    res = client.post("/admin/departments", json={"name": "Roads"}, headers=admin_headers)
    assert res.status_code == 201
    dept_id = res.json()["id"]
    assert client.post("/admin/departments", json={"name": "Roads"}, headers=admin_headers).status_code == 400

    cid = new(client, make_headers()).json()["id"]
    client.patch(f"/admin/complaints/{cid}", json={"status": "VERIFIED"}, headers=admin_headers)
    client.patch(
        f"/admin/complaints/{cid}",
        json={"status": "ASSIGNED", "department_id": dept_id},
        headers=admin_headers,
    )
    assert client.delete(f"/admin/departments/{dept_id}", headers=admin_headers).status_code == 400


def test_full_workflow(client, make_headers, admin_headers):
    citizen = make_headers()
    cid = new(client, citizen).json()["id"]
    dept = client.post("/admin/departments", json={"name": "Roads"}, headers=admin_headers).json()

    def patch(body):
        return client.patch(f"/admin/complaints/{cid}", json=body, headers=admin_headers)

    assert patch({"status": "RESOLVED", "remarks": "x"}).status_code == 400  # skipped steps
    assert patch({"status": "VERIFIED"}).status_code == 200
    assert patch({"status": "ASSIGNED"}).status_code == 400  # no department
    res = patch({"status": "ASSIGNED", "department_id": dept["id"], "priority": "HIGH"})
    assert res.status_code == 200
    assert res.json()["department_name"] == "Roads"
    assert res.json()["priority"] == "HIGH"
    assert patch({"status": "IN_PROGRESS"}).status_code == 200
    assert patch({"status": "RESOLVED"}).status_code == 400  # remarks needed
    assert patch({"status": "RESOLVED", "remarks": "Road repaired"}).status_code == 200

    timeline = client.get(f"/complaints/{cid}", headers=citizen).json()["timeline"]
    assert [t["new_status"] for t in timeline] == [
        "SUBMITTED", "VERIFIED", "ASSIGNED", "IN_PROGRESS", "RESOLVED",
    ]


def test_reject_requires_remarks(client, make_headers, admin_headers):
    cid = new(client, make_headers()).json()["id"]
    url = f"/admin/complaints/{cid}"
    assert client.patch(url, json={"status": "REJECTED"}, headers=admin_headers).status_code == 400
    ok = client.patch(
        url, json={"status": "REJECTED", "remarks": "Not a municipal issue"}, headers=admin_headers
    )
    assert ok.status_code == 200


def test_empty_patch_rejected(client, make_headers, admin_headers):
    cid = new(client, make_headers()).json()["id"]
    res = client.patch(f"/admin/complaints/{cid}", json={}, headers=admin_headers)
    assert res.status_code == 400


def test_filters(client, make_headers, admin_headers):
    h = make_headers()
    first = new(client, h).json()["id"]
    new(client, h, category="DRAINAGE", title="Drain overflowing badly")
    client.patch(f"/admin/complaints/{first}", json={"status": "VERIFIED"}, headers=admin_headers)

    by_status = client.get("/admin/complaints?status=VERIFIED", headers=admin_headers).json()
    assert [c["id"] for c in by_status] == [first]
    by_cat = client.get("/admin/complaints?category=DRAINAGE", headers=admin_headers).json()
    assert len(by_cat) == 1
    searched = client.get("/admin/complaints?q=pothole", headers=admin_headers).json()
    assert len(searched) == 1


def test_merge_syncs_status_and_hides_duplicate(client, make_headers, admin_headers):
    a, b = make_headers("a@test.com"), make_headers("b@test.com")
    id1 = new(client, a).json()["id"]
    id2 = new(client, b).json()["id"]

    res = client.post(f"/admin/complaints/{id2}/merge", json={"master_id": id1}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["master_complaint_id"] == id1

    client.patch(f"/admin/complaints/{id1}", json={"status": "VERIFIED"}, headers=admin_headers)
    assert client.get(f"/complaints/{id2}", headers=b).json()["status"] == "VERIFIED"

    # duplicates can't be edited directly
    assert client.patch(
        f"/admin/complaints/{id2}", json={"priority": "HIGH"}, headers=admin_headers
    ).status_code == 400

    public_ids = [c["id"] for c in client.get("/complaints/public").json()]
    assert id1 in public_ids and id2 not in public_ids

    dups = client.get(f"/admin/complaints/{id1}/duplicates", headers=admin_headers).json()
    assert [d["id"] for d in dups] == [id2]

    # invalid merges
    assert client.post(f"/admin/complaints/{id1}/merge", json={"master_id": id1}, headers=admin_headers).status_code == 400
    assert client.post(f"/admin/complaints/{id1}/merge", json={"master_id": id2}, headers=admin_headers).status_code == 400

    # unmerge puts it back on the public list
    assert client.post(f"/admin/complaints/{id2}/unmerge", headers=admin_headers).status_code == 200
    public_ids = [c["id"] for c in client.get("/complaints/public").json()]
    assert id2 in public_ids


def test_stats(client, make_headers, admin_headers):
    h = make_headers()
    new(client, h)
    new(client, h, category="DRAINAGE", title="Drain overflowing badly")
    stats = client.get("/admin/stats", headers=admin_headers).json()
    assert stats["total"] == 2
    assert stats["open"] == 2
    assert stats["by_status"] == {"SUBMITTED": 2}
    assert stats["by_category"] == {"ROAD": 1, "DRAINAGE": 1}
