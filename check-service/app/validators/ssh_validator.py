"""SSH configuration validator - Real validation"""

import re
from typing import Dict, Any, List, Optional
import logging

from app.validators.base import BaseValidator, ValidationContext
from app.models.schemas import ValidationResult, ValidationCheck, ValidationStatus
from app.services.docker_client import DockerClient

logger = logging.getLogger(__name__)


class SSHValidator(BaseValidator):
    """Validate SSH server configuration - реальная проверка"""

    def __init__(self, docker_client: DockerClient):
        super().__init__(
            name="SSH Configuration Validator",
            description="Validates SSH daemon configuration for security best practices",
        )
        self.docker_client = docker_client
        self._setup_checks()

    def _setup_checks(self):
        """Define SSH validation checks с весами"""
        self.checks = [
            {
                "id": "root_login",
                "name": "Root Login",
                "description": "Root login should be disabled",
                "config_key": "PermitRootLogin",
                "expected": "no",
                "points": 20,
                "command": "grep -E '^PermitRootLogin\\s+no' /etc/ssh/sshd_config",
            },
            {
                "id": "password_auth",
                "name": "Password Authentication",
                "description": "Password authentication should be disabled",
                "config_key": "PasswordAuthentication",
                "expected": "no",
                "points": 20,
                "command": "grep -E '^PasswordAuthentication\\s+no' /etc/ssh/sshd_config",
            },
            {
                "id": "ssh_port",
                "name": "SSH Port",
                "description": "SSH port should be changed to 2222",
                "config_key": "Port",
                "expected": "2222",
                "points": 20,
                "command": "grep -E '^Port\\s+2222' /etc/ssh/sshd_config",
            },
            {
                "id": "allow_users",
                "name": "AllowUsers",
                "description": "Should restrict which users can login",
                "config_key": "AllowUsers",
                "required": True,
                "points": 20,
                "command": "grep -E '^AllowUsers\\s+' /etc/ssh/sshd_config",
            },
            {
                "id": "max_auth_tries",
                "name": "Max Authentication Tries",
                "description": "Should limit authentication attempts to 3",
                "config_key": "MaxAuthTries",
                "expected_min": 1,
                "expected_max": 3,
                "points": 20,
                "command": "grep -E '^MaxAuthTries\\s+([0-9]+)' /etc/ssh/sshd_config",
            },
        ]

    async def validate(self, context: ValidationContext) -> ValidationResult:
        """Execute SSH validation - реальная проверка в контейнере"""
        logger.info(
            f"Starting REAL SSH validation for container {context.container_id}"
        )

        checks_results = []

        for check_config in self.checks:
            check = await self._check_ssh_setting(check_config, context)
            checks_results.append(check)

        total_score = self.calculate_score(checks_results)
        status = (
            ValidationStatus.PASSED if total_score >= 80 else ValidationStatus.FAILED
        )

        # Generate detailed feedback
        feedback_lines = ["SSH Hardening Validation Results:\n"]
        for check in checks_results:
            if check.status == ValidationStatus.PASSED:
                feedback_lines.append(f"  ✅ {check.name}: {check.message}")
            else:
                feedback_lines.append(f"  ❌ {check.name}: {check.message}")

        feedback_lines.append(f"\n📊 Score: {total_score:.1f}% (required: 80%)")

        if total_score >= 80:
            feedback_lines.append("\n🎉 Good job! SSH is secure!")
        else:
            feedback_lines.append("\n⚠️ Please fix the failing checks and try again.")

        feedback = "\n".join(feedback_lines)

        return ValidationResult(
            status=status,
            score=total_score,
            checks=checks_results,
            feedback=feedback,
            details={"container_id": context.container_id},
        )

    async def _check_ssh_setting(
        self, check_config: Dict[str, Any], context: ValidationContext
    ) -> ValidationCheck:
        """Проверка одного SSH параметра в контейнере"""
        check_id = check_config["id"]
        name = check_config["name"]
        max_points = check_config.get("points", 20)
        command = check_config.get("command")

        if not command:
            return self.create_check(
                check_id,
                name,
                ValidationStatus.ERROR,
                f"No check command defined",
                0,
                max_points,
            )

        try:
            result = await self._execute_check(command, context)

            if result.get("exit_code") == 0 and result.get("stdout", "").strip():
                return self.create_check(
                    check_id,
                    name,
                    ValidationStatus.PASSED,
                    f"✅ Correct",
                    max_points,
                    max_points,
                )
            else:
                return self.create_check(
                    check_id,
                    name,
                    ValidationStatus.FAILED,
                    f"❌ Not configured correctly",
                    0,
                    max_points,
                )

        except Exception as e:
            logger.error(f"Check {check_id} failed: {e}")
            return self.create_check(
                check_id,
                name,
                ValidationStatus.ERROR,
                f"Check error: {str(e)}",
                0,
                max_points,
            )

    async def _execute_check(
        self, command: str, context: ValidationContext
    ) -> Dict[str, Any]:
        """Execute a check in container"""
        return await self.docker_client.exec_command(context.container_id, command)
