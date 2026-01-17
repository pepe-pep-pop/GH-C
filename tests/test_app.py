"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    initial_state = {
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
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and friendly tournaments",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through experiments and projects",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and various art mediums",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater productions and acting workshops",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(initial_state)
    yield
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
    
    def test_get_activities_participants_are_strings(self, client, reset_activities):
        """Test that participants are email strings"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post("/activities/Tennis%20Club/signup?email=newemail@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newemail@mergington.edu" in data["message"]
        
        # Verify the user was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newemail@mergington.edu" in activities_data["Tennis Club"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        # michael@mergington.edu is already in Chess Club
        response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_different_activities(self, client, reset_activities):
        """Test that same student can signup for multiple activities"""
        email = "newemail@mergington.edu"
        
        # Sign up for Tennis Club
        response1 = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Chess Club
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Tennis Club"]["participants"]
        assert email in activities_data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        # michael@mergington.edu is in Chess Club
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        
        # Verify the user was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_signed_up(self, client, reset_activities):
        """Test unregister for student not in the activity"""
        response = client.delete("/activities/Chess%20Club/unregister?email=nosuch@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up then unregistering"""
        email = "test@mergington.edu"
        activity = "Tennis%20Club"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify the user was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Tennis Club"]["participants"]


class TestActivityCapacity:
    """Tests for activity capacity constraints"""
    
    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that participant count is correctly tracked"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Tennis Club has 0 participants
        assert len(data["Tennis Club"]["participants"]) == 0
        assert data["Tennis Club"]["max_participants"] == 10
        
        # Sign up a student
        client.post("/activities/Tennis%20Club/signup?email=new@mergington.edu")
        
        # Check updated count
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        assert len(updated_data["Tennis Club"]["participants"]) == 1
