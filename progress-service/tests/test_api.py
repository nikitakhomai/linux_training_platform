"""API tests for Progress Service"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "progress-service"
    assert data["status"] == "operational"
    print("✅ Root endpoint passed")


def test_submit_task():
    """Test task submission"""
    response = client.post(
        "/api/v1/progress/submit",
        json={"task_id": 1, "user_id": 1, "score": 85.5, "passed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recorded"] is True
    print("✅ Task submission passed")


def test_get_user_progress():
    """Test getting user progress"""
    # First submit a task to create progress
    client.post(
        "/api/v1/progress/submit",
        json={"task_id": 1, "user_id": 1, "score": 85.5, "passed": True},
    )

    response = client.get("/api/v1/progress/user/1")
    assert response.status_code == 200
    data = response.json()

    # Check fields - NO 'id' field
    assert "user_id" in data
    assert "total_score" in data
    assert "skills" in data
    assert "courses_progress" in data
    assert "recommendations" in data
    assert isinstance(data["skills"], list)
    assert isinstance(data["courses_progress"], list)

    print(f"✅ User progress passed - user_id: {data['user_id']}")


def test_get_progress_summary():
    """Test getting progress summary"""
    # First submit a task
    client.post(
        "/api/v1/progress/submit",
        json={"task_id": 1, "user_id": 1, "score": 85.5, "passed": True},
    )

    response = client.get("/api/v1/progress/summary")
    assert response.status_code == 200
    data = response.json()

    # Check fields - NO 'id' field
    required_fields = [
        "user_id",
        "total_tasks_completed",
        "total_courses_completed",
        "average_score",
        "current_streak",
        "best_streak",
        "total_points",
        "rank",
    ]
    for field in required_fields:
        assert field in data

    print(f"✅ Progress summary passed - user_id: {data['user_id']}")


def test_get_leaderboard():
    """Test getting leaderboard"""
    response = client.get("/api/v1/leaderboard/?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Leaderboard passed - entries: {len(data)}")


def test_get_task_statistics():
    """Test getting task statistics"""
    response = client.get("/api/v1/analytics/tasks/1/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == 1
    print("✅ Task statistics passed")


def test_get_overall_statistics():
    """Test getting overall statistics"""
    response = client.get("/api/v1/analytics/overall")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    print("✅ Overall statistics passed")


def test_get_skills_distribution():
    """Test getting skills distribution"""
    response = client.get("/api/v1/analytics/skills/distribution")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    print("✅ Skills distribution passed")


def test_get_user_rank():
    """Test getting user rank"""
    response = client.get("/api/v1/leaderboard/user/1/rank")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "rank" in data
    print(f"✅ User rank passed")


def test_submit_task_with_low_score():
    """Test submitting failed task"""
    response = client.post(
        "/api/v1/progress/submit",
        json={"task_id": 2, "user_id": 1, "score": 45.0, "passed": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recorded"] is True
    print("✅ Failed task submission passed")


def test_multiple_submissions():
    """Test multiple submissions for same task"""
    # First submission
    client.post(
        "/api/v1/progress/submit",
        json={"task_id": 3, "user_id": 1, "score": 60.0, "passed": False},
    )

    # Second submission with better score
    client.post(
        "/api/v1/progress/submit",
        json={"task_id": 3, "user_id": 1, "score": 95.0, "passed": True},
    )

    # Check progress to verify best score is kept
    progress = client.get("/api/v1/progress/user/1")
    assert progress.status_code == 200
    data = progress.json()

    # Find task 3 in courses
    found = False
    for course in data.get("courses_progress", []):
        for task in course.get("tasks", []):
            if task.get("task_id") == 3:
                assert task.get("best_score") == 95.0
                assert task.get("attempts") >= 2
                found = True
                break

    assert found
    print("✅ Multiple submissions passed")


def test_different_users():
    """Test progress for different users"""
    # Submit for user 1
    client.post(
        "/api/v1/progress/submit",
        json={"task_id": 1, "user_id": 1, "score": 90.0, "passed": True},
    )

    # Submit for user 2
    client.post(
        "/api/v1/progress/submit",
        json={"task_id": 1, "user_id": 2, "score": 75.0, "passed": True},
    )

    # Check user 1 progress
    resp1 = client.get("/api/v1/progress/user/1")
    assert resp1.status_code == 200
    data1 = resp1.json()

    # Check user 2 progress
    resp2 = client.get("/api/v1/progress/user/2")
    assert resp2.status_code == 200
    data2 = resp2.json()

    # Verify both users have user_id field
    assert "user_id" in data1
    assert "user_id" in data2

    # Verify they are different users
    assert data1["user_id"] != data2["user_id"]

    print(f"✅ Different users test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
