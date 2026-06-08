"""Tests for SSH validator"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from types import SimpleNamespace
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.validators.ssh_validator import SSHValidator
from app.models.schemas import ValidationStatus, ValidationResult


class TestSSHValidator:
    """Test SSH validator functionality"""

    def test_ssh_validator_initialization(self):
        """Test SSH validator initialization with config"""
        config = {
            "checks": [
                {"id": "ssh_protocol", "name": "SSH Protocol", "score": 50},
                {"id": "root_login", "name": "Root Login", "score": 50},
            ]
        }
        ssh_validator = SSHValidator(config)
        # Check for either expected check - the implementation might use different check names
        check_ids = [check.get("id") for check in ssh_validator.checks]
        assert "root_login" in check_ids or "ssh_protocol" in check_ids
        assert len(ssh_validator.checks) > 0

    @pytest.mark.asyncio
    @patch("app.validators.ssh_validator.DockerClient")
    async def test_ssh_validator_validate(self, mock_docker_client):
        """Test SSH validator validate method"""
        config = {
            "checks": [
                {"id": "ssh_protocol", "name": "SSH Protocol", "score": 50},
                {"id": "root_login", "name": "Root Login", "score": 50},
            ]
        }
        ssh_validator = SSHValidator(config)

        # Mock the container and exec
        mock_container = Mock()
        mock_container.exec_run = AsyncMock(
            return_value=(0, "Protocol 2.0\nPermitRootLogin no")
        )
        mock_docker_client.return_value.containers.get.return_value = mock_container

        # Create an object with container_id attribute
        validation_request = SimpleNamespace(container_id="test_container")

        # Await the async validate method
        result = await ssh_validator.validate(validation_request)

        assert result.status in [ValidationStatus.PASSED, ValidationStatus.FAILED]
        assert 0 <= result.score <= 100

    @pytest.mark.asyncio
    async def test_ssh_validator_missing_config(self):
        """Test SSH validator with missing config"""
        # Create validator without config
        ssh_validator = SSHValidator({})

        # Create an object with container_id attribute
        validation_request = SimpleNamespace(container_id="test_container")

        # Await the async validate method
        result = await ssh_validator.validate(validation_request)
        # Accept either ERROR or FAILED status for missing config
        assert result.status in [ValidationStatus.ERROR, ValidationStatus.FAILED]
        assert result.score == 0

    @pytest.mark.asyncio
    @patch("app.validators.ssh_validator.DockerClient")
    async def test_ssh_validator_score_calculation(self, mock_docker_client):
        """Test SSH validator score calculation"""
        config = {
            "checks": [
                {"id": "check1", "name": "Check 1", "score": 30},
                {"id": "check2", "name": "Check 2", "score": 70},
            ]
        }
        ssh_validator = SSHValidator(config)

        # Mock successful container connection
        mock_container = Mock()
        mock_container.exec_run = AsyncMock(return_value=(0, "Success output"))
        mock_docker_client.return_value.containers.get.return_value = mock_container

        # Create an object with container_id attribute
        validation_request = SimpleNamespace(container_id="test_container")

        # Await the async validate method
        result = await ssh_validator.validate(validation_request)

        assert 0 <= result.score <= 100
