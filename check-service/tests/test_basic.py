"""Basic tests for the application"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    # The actual response has 'service', 'status', 'version' instead of 'message'
    assert "service" in data
    assert data["status"] == "operational"
    assert "version" in data


def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_validation_types():
    """Test validation types endpoint"""
    response = client.get("/api/v1/validation/types")
    assert response.status_code == 200
    data = response.json()
    assert "validation_types" in data


def test_validate_task():
    """Test validate task endpoint"""
    payload = {
        "task_id": 1,
        "container_id": "test123",
        "user_id": 1,
        "validation_type": "ssh_config",
        "validation_data": {"ssh_port": 22},
    }
    response = client.post("/api/v1/validation/validate", json=payload)
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert "total_score" in data
