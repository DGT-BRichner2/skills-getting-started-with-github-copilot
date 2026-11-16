"""
FastAPI tests for Mergington High School Activities API
Using AAA (Arrange-Act-Assert) pattern
"""
import pytest


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_activities_successful(self, client, fresh_activities):
        # Arrange
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_contains_all_activities(self, client, fresh_activities):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_response_structure(self, client, fresh_activities):
        # Arrange
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_includes_participants(self, client, fresh_activities):
        # Arrange
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert len(chess_club["participants"]) > 0
    
    def test_get_activities_max_participants_field(self, client, fresh_activities):
        # Arrange
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_data in data.values():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestSignupEndpoint:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, fresh_activities):
        # Arrange
        activity_name = "Basketball Team"
        email = "john@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in fresh_activities[activity_name]["participants"]
    
    def test_signup_adds_participant_to_list(self, client, fresh_activities):
        # Arrange
        activity_name = "Basketball Team"
        email = "alice@test.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_duplicate_error(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client, fresh_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_multiple_students(self, client, fresh_activities):
        # Arrange
        activity_name = "Track and Field"
        emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert
        for email in emails:
            assert email in fresh_activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Test DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
    
    def test_unregister_removes_participant(self, client, fresh_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_nonexistent_activity(self, client, fresh_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
    
    def test_unregister_then_resign_up(self, client, fresh_activities):
        # Arrange
        activity_name = "Drama Club"
        email = "actor@test.edu"
        
        # Act - Sign up
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        # Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        # Sign up again
        response3 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_signup_unregister_flow(self, client, fresh_activities):
        # Arrange
        activity_name = "Debate Club"
        email = "debater@test.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        # Get activities to verify signup
        get_response1 = client.get("/activities")
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        # Get activities to verify unregister
        get_response2 = client.get("/activities")
        
        # Assert
        assert signup_response.status_code == 200
        assert get_response1.status_code == 200
        assert email in get_response1.json()[activity_name]["participants"]
        
        assert unregister_response.status_code == 200
        assert get_response2.status_code == 200
        assert email not in get_response2.json()[activity_name]["participants"]
    
    def test_participant_list_updates_across_operations(self, client, fresh_activities):
        # Arrange
        activity_name = "Science Club"
        emails = ["scientist1@test.edu", "scientist2@test.edu"]
        
        # Act & Assert - Verify initial state
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        
        # Sign up first student
        client.post(f"/activities/{activity_name}/signup?email={emails[0]}")
        response = client.get("/activities")
        assert emails[0] in response.json()[activity_name]["participants"]
        
        # Sign up second student
        client.post(f"/activities/{activity_name}/signup?email={emails[1]}")
        response = client.get("/activities")
        assert emails[1] in response.json()[activity_name]["participants"]
        
        # Unregister first student
        client.delete(f"/activities/{activity_name}/unregister?email={emails[0]}")
        response = client.get("/activities")
        assert emails[0] not in response.json()[activity_name]["participants"]
        assert emails[1] in response.json()[activity_name]["participants"]
