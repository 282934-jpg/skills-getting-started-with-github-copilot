import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset the activities database to initial state before each test."""
    global activities
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in local tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Learn soccer techniques and play friendly matches",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        }
    }


# AAA Tests for GET /

def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html."""
    # Arrange - client fixture provides test client

    # Act - make GET request to root
    response = client.get("/")

    # Assert - verify redirect status and location
    assert response.status_code == 302
    assert response.headers["location"] == "/static/index.html"


# AAA Tests for GET /activities

def test_get_activities(client):
    """Test that get_activities returns all activities with correct structure."""
    # Arrange - client fixture and reset_activities fixture ensure clean state

    # Act - make GET request to activities endpoint
    response = client.get("/activities")

    # Assert - verify response status and content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 5  # All activities present
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert len(data["Chess Club"]["participants"]) == 2  # Initial participants


# AAA Tests for POST /activities/{activity_name}/signup

def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange - select activity with available spots and new email
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"

    # Act - make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert - verify success response and participant added
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    """Test signup fails for non-existent activity."""
    # Arrange - use invalid activity name
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act - attempt signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert - verify 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_registration(client):
    """Test signup fails when student is already registered."""
    # Arrange - use activity and email already registered
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act - attempt duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert - verify 400 error
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already registered for this activity"}


# AAA Tests for DELETE /activities/{activity_name}/participants/{email}

def test_remove_participant_success(client):
    """Test successful removal of a participant."""
    # Arrange - select activity and existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act - make DELETE request
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert - verify success and participant removed
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_activity_not_found(client):
    """Test removal fails for non-existent activity."""
    # Arrange - use invalid activity name
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act - attempt removal
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert - verify 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_not_registered(client):
    """Test removal fails when student is not registered."""
    # Arrange - use activity and email not in participants
    activity_name = "Basketball Team"  # Empty participants
    email = "notregistered@mergington.edu"

    # Act - attempt removal
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert - verify 400 error
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not registered for this activity"}