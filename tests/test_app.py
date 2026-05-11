from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities():
    reset_activities()
    client = TestClient(app)

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity():
    reset_activities()
    client = TestClient(app)

    response = client.post(
        f"/activities/{quote('Chess Club')}/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up newstudent@mergington.edu for Chess Club"}
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    reset_activities()
    client = TestClient(app)

    response = client.post(
        f"/activities/{quote('Chess Club')}/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant():
    reset_activities()
    client = TestClient(app)

    response = client.delete(
        f"/activities/{quote('Chess Club')}/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    reset_activities()
    client = TestClient(app)

    response = client.delete(
        f"/activities/{quote('Chess Club')}/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
