"""Tests for validation API endpoints"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.main import app


client = TestClient(app)


class TestValidationAPI:
    """Test validation API endpoints"""

    def test_validation_types_endpoint(self):
        """Test GET /api/v1/validation/types"""
        response = client.get("/api/v1/validation/types")
        assert response.status_code == 200
        data = response.json()
        assert "validation_types" in data
        assert isinstance(data["validation_types"], list)

    def test_validate_endpoint_success(self):
        """Test POST /api/v1/validation/validate - success case"""
        payload = {
            "task_id": 1,
            "container_id": "test123",
            "user_id": 1,
            "validation_type": "ssh_config",
        }
        response = client.post("/api/v1/validation/validate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["passed", "failed"]
        assert "total_score" in data

    def test_validate_endpoint_with_different_types(self):
        """Test validation with different types"""
        types = ["ssh_config", "file_permissions", "firewall_rules"]

        for vtype in types:
            payload = {
                "task_id": 1,
                "container_id": "test123",
                "user_id": 1,
                "validation_type": vtype,
            }
            response = client.post("/api/v1/validation/validate", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["passed", "failed"]
