import importlib

import pytest


@pytest.fixture
def client():
    # Reload the app module to reset in-memory state between tests
    import src.app as app_module
    importlib.reload(app_module)
    from fastapi.testclient import TestClient

    return TestClient(app_module.app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Art Club" in data


def test_signup_and_unregister_flow(client):
    email = "test@example.com"
    activity = "Art Club"

    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert f"Signed up {email}" in r.json()["message"]

    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    r = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r.status_code == 200

    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_signup_nonexistent_activity(client):
    r = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert r.status_code == 404


def test_double_signup_returns_400(client):
    email = "dup@example.com"
    activity = "Art Club"

    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200

    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400


def test_activity_full(client):
    activity = "Art Club"

    r = client.get("/activities")
    maxp = r.json()[activity]["max_participants"]

    for i in range(maxp):
        r = client.post(f"/activities/{activity}/signup", params={"email": f"user{i}@test"})
        assert r.status_code == 200

    r = client.post(f"/activities/{activity}/signup", params={"email": "overflow@test"})
    assert r.status_code == 400
