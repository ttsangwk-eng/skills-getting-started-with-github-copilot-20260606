from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_activities():
    yield
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    json_data = response.json()
    assert "Chess Club" in json_data
    assert "Programming Class" in json_data
    assert isinstance(json_data["Chess Club"]["participants"], list)


def test_signup_for_activity():
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    email = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "unknown@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
