"""Tests for SSH validator"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.validators.ssh_validator import SSHValidator
from app.validators.base import ValidationContext
from app.models.schemas import ValidationStatus
from app.services.docker_client import DockerClient


@pytest.fixture
def docker_client():
    """Create mock Docker client"""
    client = AsyncMock(spec=DockerClient)

    async def exec_command(container_id, command, timeout=30):
        # Mock SSH config content
        if "sshd_config" in command:
            return {
                "stdout": """
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PermitEmptyPasswords no
MaxAuthTries 3
PubkeyAuthentication yes
X11Forwarding no
ClientAliveInterval 300
""",
                "stderr": "",
                "exit_code": 0,
            }
        return {"stdout": "", "stderr": "", "exit_code": 0}

    client.exec_command = exec_command
    return client


@pytest.fixture
def ssh_validator(docker_client):
    """Create SSH validator instance"""
    return SSHValidator(docker_client)


@pytest.fixture
def validation_context():
    """Create validation context"""
    return ValidationContext(
        container_id="test_container", task_id=1, user_id=1, validation_config={}
    )


@pytest.mark.asyncio
async def test_ssh_validator_initialization(ssh_validator):
    """Test SSH validator initialization"""
    assert ssh_validator.name == "SSH Configuration Validator"
    assert len(ssh_validator.checks) > 0
    assert ssh_validator.checks[0]["id"] == "ssh_protocol"


@pytest.mark.asyncio
async def test_ssh_validator_validate(ssh_validator, validation_context):
    """Test SSH validation execution"""
    result = await ssh_validator.validate(validation_context)

    assert result is not None
    assert result.status == ValidationStatus.PASSED
    assert result.score > 0
    assert len(result.checks) > 0
    assert result.feedback is not None


@pytest.mark.asyncio
async def test_ssh_validator_missing_config(docker_client, validation_context):
    """Test SSH validation with missing config"""

    async def exec_command_error(container_id, command, timeout=30):
        return {"stdout": "", "stderr": "No such file", "exit_code": 1}

    docker_client.exec_command = exec_command_error
    validator = SSHValidator(docker_client)

    result = await validator.validate(validation_context)

    assert result.status == ValidationStatus.ERROR
    assert result.score == 0


@pytest.mark.asyncio
async def test_ssh_validator_check_creation(ssh_validator):
    """Test creation of validation checks"""
    check = ssh_validator.create_check(
        check_id="test_check",
        name="Test Check",
        status=ValidationStatus.PASSED,
        message="Test passed",
        points=10,
        max_points=10,
    )

    assert check.check_id == "test_check"
    assert check.name == "Test Check"
    assert check.status == ValidationStatus.PASSED
    assert check.points == 10
    assert check.max_points == 10
    assert check.score == 100.0


@pytest.mark.asyncio
async def test_ssh_validator_score_calculation(ssh_validator):
    """Test score calculation"""
    from app.models.schemas import ValidationCheck, ValidationStatus

    checks = [
        ValidationCheck(
            check_id="c1",
            name="Check 1",
            status=ValidationStatus.PASSED,
            message="Passed",
            points=10,
            max_points=10,
        ),
        ValidationCheck(
            check_id="c2",
            name="Check 2",
            status=ValidationStatus.FAILED,
            message="Failed",
            points=0,
            max_points=10,
        ),
    ]

    score = ssh_validator.calculate_score(checks)
    assert score == 50.0
