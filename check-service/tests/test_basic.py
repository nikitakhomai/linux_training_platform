"""Basic tests for Check Service"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Linux Security Check Service"
    assert data["status"] == "operational"


def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_validation_types():
    """Test validation types endpoint"""
    response = client.get("/api/v1/validation/types")
    assert response.status_code == 200
    data = response.json()
    assert "validation_types" in data
    assert len(data["validation_types"]) > 0


def test_validate_task():
    """Test validation endpoint"""
    request_data = {
        "task_id": 1,
        "container_id": "test123",
        "user_id": 1,
        "validation_type": "ssh_config",
    }
    response = client.post("/api/v1/validation/validate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "passed"
    assert "total_score" in data
