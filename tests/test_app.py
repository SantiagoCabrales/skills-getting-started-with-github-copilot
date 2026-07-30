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


def test_unregister_existing_participant(client):
    response = client.delete(
        "/activities/Programming%20Class/signup?email=emma@mergington.edu"
    )

    assert response.status_code == 200
    assert "emma@mergington.edu" not in app_module.activities["Programming Class"]["participants"]
    assert response.json()["message"] == "Unregistered emma@mergington.edu from Programming Class"
