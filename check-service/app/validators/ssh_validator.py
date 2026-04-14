"""SSH configuration validator"""

import re
from typing import Dict, Any, List, Optional
import logging

from app.validators.base import BaseValidator, ValidationContext
from app.models.schemas import ValidationResult, ValidationCheck, ValidationStatus
from app.services.docker_client import DockerClient


logger = logging.getLogger(__name__)


class SSHValidator(BaseValidator):
    """Validate SSH server configuration"""

    def __init__(self, docker_client: DockerClient):
        super().__init__(
            name="SSH Configuration Validator",
            description="Validates SSH daemon configuration for security best practices",
        )
        self.docker_client = docker_client
        self._setup_checks()

    def _setup_checks(self):
        """Define SSH validation checks"""
        self.checks = [
            {
                "id": "ssh_protocol",
                "name": "SSH Protocol Version",
                "description": "SSH protocol version should be 2 only",
                "config_key": "Protocol",
                "expected": "2",
                "points": 10,
            },
            {
                "id": "root_login",
                "name": "Root Login",
                "description": "Root login should be disabled",
                "config_key": "PermitRootLogin",
                "expected": "no",
                "points": 15,
            },
            {
                "id": "password_auth",
                "name": "Password Authentication",
                "description": "Password authentication should be disabled (use keys)",
                "config_key": "PasswordAuthentication",
                "expected": "no",
                "points": 15,
            },
            {
                "id": "empty_passwords",
                "name": "Empty Passwords",
                "description": "Empty passwords should not be allowed",
                "config_key": "PermitEmptyPasswords",
                "expected": "no",
                "points": 10,
            },
            {
                "id": "max_auth_tries",
                "name": "Max Authentication Tries",
                "description": "Maximum authentication attempts should be limited",
                "config_key": "MaxAuthTries",
                "expected_min": 3,
                "expected_max": 6,
                "points": 10,
            },
            {
                "id": "allow_users",
                "name": "Allowed Users",
                "description": "Should restrict which users can login via SSH",
                "config_key": "AllowUsers",
                "required": False,
                "points": 10,
            },
            {
                "id": "pubkey_auth",
                "name": "Public Key Authentication",
                "description": "Public key authentication should be enabled",
                "config_key": "PubkeyAuthentication",
                "expected": "yes",
                "points": 10,
            },
            {
                "id": "x11_forwarding",
                "name": "X11 Forwarding",
                "description": "X11 forwarding should be disabled",
                "config_key": "X11Forwarding",
                "expected": "no",
                "points": 5,
            },
            {
                "id": "client_alive_interval",
                "name": "Client Alive Interval",
                "description": "Should have client alive timeout configured",
                "config_key": "ClientAliveInterval",
                "expected_min": 300,
                "expected_max": 600,
                "points": 5,
            },
            {
                "id": "banner",
                "name": "Login Banner",
                "description": "Should display a login banner",
                "config_key": "Banner",
                "required": False,
                "points": 5,
            },
        ]

    async def validate(self, context: ValidationContext) -> ValidationResult:
        """Execute SSH validation"""
        logger.info(f"Starting SSH validation for container {context.container_id}")

        checks_results = []

        # Get SSH config from container
        ssh_config = await self._get_ssh_config(context)

        if not ssh_config:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                score=0,
                checks=[],
                feedback="Unable to read SSH configuration file",
                details={"error": "ssh_config_not_found"},
            )

        # Execute each check
        for check_config in self.checks:
            check = await self._validate_ssh_setting(check_config, ssh_config, context)
            checks_results.append(check)

        # Calculate results
        total_score = self.calculate_score(checks_results)
        status = (
            ValidationStatus.PASSED if total_score >= 70 else ValidationStatus.FAILED
        )
        feedback = self.generate_feedback(checks_results)

        return ValidationResult(
            status=status,
            score=total_score,
            checks=checks_results,
            feedback=feedback,
            details={"ssh_config": ssh_config},
        )

    async def _get_ssh_config(self, context: ValidationContext) -> Dict[str, str]:
        """Extract SSH configuration from container"""
        try:
            # Try common SSH config locations
            locations = ["/etc/ssh/sshd_config", "/etc/ssh/sshd_config.d/*.conf"]

            config_content = ""
            for location in locations:
                result = await self.docker_client.exec_command(
                    context.container_id, f"cat {location} 2>/dev/null || true"
                )
                config_content += result.get("stdout", "")

            if not config_content:
                return {}

            # Parse config
            config = {}
            for line in config_content.split("\n"):
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Parse key-value pairs
                if " " in line:
                    key, value = line.split(" ", 1)
                    # Handle multiple values
                    if "," in value:
                        value = [v.strip() for v in value.split(",")]
                    config[key] = value

            return config

        except Exception as e:
            logger.error(f"Error reading SSH config: {e}")
            return {}

    async def _validate_ssh_setting(
        self,
        check_config: Dict[str, Any],
        ssh_config: Dict[str, Any],
        context: ValidationContext,
    ) -> ValidationCheck:
        """Validate a single SSH setting"""
        check_id = check_config["id"]
        name = check_config["name"]
        points = 0
        max_points = check_config.get("points", 10)

        config_key = check_config.get("config_key")
        expected = check_config.get("expected")
        expected_min = check_config.get("expected_min")
        expected_max = check_config.get("expected_max")
        required = check_config.get("required", True)

        # Check if setting exists
        if config_key not in ssh_config:
            if not required:
                return self.create_check(
                    check_id,
                    name,
                    ValidationStatus.PASSED,
                    f"{name}: Not configured (optional)",
                    max_points,
                    max_points,
                )
            else:
                return self.create_check(
                    check_id,
                    name,
                    ValidationStatus.FAILED,
                    f"{name}: Setting '{config_key}' not found in SSH config",
                    0,
                    max_points,
                )

        value = ssh_config[config_key]

        # Validate based on type
        if expected is not None:
            # Exact match validation
            if str(value).lower() == str(expected).lower():
                points = max_points
                message = f"{name}: Correct value '{value}'"
            else:
                message = f"{name}: Expected '{expected}', got '{value}'"

        elif expected_min is not None and expected_max is not None:
            # Range validation
            try:
                num_value = int(value)
                if expected_min <= num_value <= expected_max:
                    points = max_points
                    message = f"{name}: Value {value} is within allowed range"
                else:
                    message = f"{name}: Value {value} outside range [{expected_min}, {expected_max}]"
            except ValueError:
                message = f"{name}: Invalid numeric value '{value}'"

        else:
            # Custom validation
            points = max_points
            message = f"{name}: Configuration present"

        status = (
            ValidationStatus.PASSED if points == max_points else ValidationStatus.FAILED
        )

        return self.create_check(
            check_id,
            name,
            status,
            message,
            points,
            max_points,
            details={
                "current_value": value,
                "expected": expected or f"{expected_min}-{expected_max}",
            },
        )

    async def _execute_check(
        self, command: str, context: ValidationContext
    ) -> Dict[str, Any]:
        """Execute a command in container"""
        return await self.docker_client.exec_command(context.container_id, command)
