PAYLOAD = {
    "industry": "pharmacy",
    "bill": {"units": 20000, "amount": 170000, "days": 30},
    "hours": {"hvac": 20, "compressor": 8, "fbd": 6, "tablet": 10, "chiller": 18},
}


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_register_and_duplicate(client):
    body = {"name": "Test User", "email": "t@test.com", "password": "Password123"}
    assert client.post("/api/auth/register", json=body).status_code == 201
    assert client.post("/api/auth/register", json=body).status_code == 409


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", data={"username": "admin@test.com", "password": "nope"})
    assert r.status_code == 401


def test_analysis_requires_auth(client):
    assert client.post("/api/analysis", json=PAYLOAD).status_code == 401


def test_analysis_totals_match_bill(client, auth):
    r = client.post("/api/analysis", json=PAYLOAD, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert any(row["name"] == "Others" for row in data["rows"])
    assert abs(sum(row["units"] for row in data["rows"]) - 20000) <= len(data["rows"])
    assert len(data["ai"]["forecast"]["units"]) == 3


def test_invalid_hours_rejected(client, auth):
    bad = {**PAYLOAD, "hours": {"hvac": 30}}
    assert client.post("/api/analysis", json=bad, headers=auth).status_code == 422


def test_reports(client, auth):
    for fmt, ctype in (("csv", "text/csv"), ("xlsx", "spreadsheetml"), ("pdf", "application/pdf")):
        r = client.post(f"/api/reports/{fmt}", json=PAYLOAD, headers=auth)
        assert r.status_code == 200 and ctype in r.headers["content-type"]
        assert len(r.content) > 100