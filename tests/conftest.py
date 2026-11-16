import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Provide a fresh copy of activities for each test"""
    original_activities = {}
    for activity_name, activity_data in activities.items():
        original_activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
    
    activities.clear()
    for activity_name, activity_data in original_activities.items():
        activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
    
    yield activities
    
    activities.clear()
    for activity_name, activity_data in original_activities.items():
        activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
