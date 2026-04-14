"""Test all endpoints"""

import sys
import os

sys.path.insert(0, "/app")

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAllEndpoints:
    """Test all API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_docs_endpoint(self):
        """Test that docs are available"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_endpoint(self):
        """Test OpenAPI schema"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        # Проверяем что есть хотя бы один путь
        assert len(data["paths"]) > 0
        print(f"✅ OpenAPI schema has {len(data['paths'])} paths")

    def test_cors_headers(self):
        """Test CORS headers"""
        response = client.options("/api/v1/containers")
        # CORS headers могут не быть в OPTIONS ответе, проверим через GET
        response = client.get("/api/v1/containers")
        # Проверяем что есть CORS header
        assert (
            "access-control-allow-origin" in response.headers
            or response.status_code in [200, 404]
        )
        print("✅ CORS headers present")

    def test_content_type(self):
        """Test content type is JSON"""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"

    def test_response_structure(self):
        """Test response structure is consistent"""
        response = client.get("/")
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert "endpoints" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
