import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)
    yield
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_mapping(client):
    response = client.get("/activities")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert "Chess Club" in body


def test_signup_for_activity_success(client):
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    body = response.json()
    assert "message" in body

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_for_activity_rejects_duplicate_student(client):
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": "michael@mergington.edu"}
    )

    assert response.status_code == 400
    body = response.json()
    assert "detail" in body


def test_signup_for_activity_returns_not_found_for_unknown_activity(client):
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "test@mergington.edu"})

    assert response.status_code == 404
    body = response.json()
    assert "detail" in body


def test_unregister_from_activity_success(client):
    email = "daniel@mergington.edu"

    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})

    assert response.status_code == 200
    body = response.json()
    assert "message" in body

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_from_activity_returns_not_found_for_unregistered_student(client):
    response = client.delete(
        "/activities/Chess%20Club/participants", params={"email": "not.registered@mergington.edu"}
    )

    assert response.status_code == 404
    body = response.json()
    assert "detail" in body


def test_unregister_from_activity_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/participants", params={"email": "test@mergington.edu"}
    )

    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
