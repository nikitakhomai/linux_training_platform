"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.services.validator import ValidationService
from app.services.docker_client import DockerClient


@pytest.fixture
def client():
    """Test client fixture"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_docker_client():
    """Mock Docker client"""
    mock = AsyncMock(spec=DockerClient)

    async def mock_exec_command(container_id, command, timeout=30):
        return {"stdout": "test output", "stderr": "", "exit_code": 0}

    mock.exec_command = mock_exec_command

    async def mock_container_exists(container_id):
        return True

    mock.container_exists = mock_container_exists

    return mock


@pytest.fixture
def mock_validation_service(mock_docker_client):
    """Mock validation service"""
    service = ValidationService(mock_docker_client)

    # Mock validate method
    async def mock_validate(request):
        from app.models.schemas import (
            ValidationResponse,
            ValidationStatus,
            ValidationCheck,
        )
        import uuid
        from datetime import datetime

        return ValidationResponse(
            validation_id=str(uuid.uuid4()),
            task_id=request.task_id,
            user_id=request.user_id,
            status=ValidationStatus.PASSED,
            total_score=85.0,
            checks=[
                ValidationCheck(
                    check_id="test_1",
                    name="Test Check 1",
                    status=ValidationStatus.PASSED,
                    message="Passed",
                    points=10,
                    max_points=10,
                )
            ],
            feedback="Test feedback",
            details={},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=100,
        )

    service.validate = mock_validate

    return service


@pytest.fixture
def sample_validation_request():
    """Sample validation request"""
    from app.models.schemas import ValidationRequest, ValidationType

    return ValidationRequest(
        task_id=1,
        container_id="abc123def456",
        user_id=1,
        validation_type=ValidationType.SSH_CONFIG,
    )
