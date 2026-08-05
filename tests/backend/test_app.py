import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_root_redirects_to_frontend(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Programming Class" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant(client):
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )

    assert response.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"


def test_signup_for_missing_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown%20Club/signup?email=test@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_existing_participant(client):
    response = client.delete(
        "/activities/Programming%20Class/signup?email=emma@mergington.edu"
    )

    assert response.status_code == 200
    assert "emma@mergington.edu" not in app_module.activities["Programming Class"]["participants"]
    assert response.json()["message"] == "Unregistered emma@mergington.edu from Programming Class"


def test_unregister_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/signup?email=unknown@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
