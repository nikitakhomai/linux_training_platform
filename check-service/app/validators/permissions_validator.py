"""File permissions validator"""

from typing import Dict, Any
import logging
from app.validators.base import BaseValidator, ValidationContext
from app.models.schemas import ValidationResult, ValidationStatus, ValidationCheck
from app.services.docker_client import DockerClient

logger = logging.getLogger(__name__)


class PermissionsValidator(BaseValidator):
    """Validate file and directory permissions"""

    def __init__(self, docker_client: DockerClient):
        super().__init__(
            name="File Permissions Validator",
            description="Validates file and directory permissions",
        )
        self.docker_client = docker_client

    async def validate(self, context: ValidationContext) -> ValidationResult:
        """Execute permissions validation"""
        logger.info(
            f"Starting permissions validation for container {context.container_id}"
        )

        checks = []

        # Check critical files
        critical_files = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/ssh/sshd_config",
            "/etc/sudoers",
        ]

        for file_path in critical_files:
            check = await self._check_file_permissions(file_path, context)
            checks.append(check)

        # Calculate results
        total_score = self.calculate_score(checks)
        status = (
            ValidationStatus.PASSED if total_score >= 70 else ValidationStatus.FAILED
        )
        feedback = self.generate_feedback(checks)

        return ValidationResult(
            status=status,
            score=total_score,
            checks=checks,
            feedback=feedback,
            details={"checked_files": critical_files},
        )

    async def _check_file_permissions(
        self, file_path: str, context: ValidationContext
    ) -> ValidationCheck:
        """Check permissions for a single file"""
        try:
            result = await self.docker_client.exec_command(
                context.container_id,
                f"ls -l {file_path} 2>/dev/null || echo 'NOT_FOUND'",
            )

            output = result.get("stdout", "").strip()

            if "NOT_FOUND" in output or not output:
                return self.create_check(
                    f"file_{file_path.replace('/', '_')}",
                    f"File {file_path}",
                    ValidationStatus.FAILED,
                    f"File {file_path} not found",
                    0,
                    10,
                )

            # Parse permissions
            parts = output.split()
            if len(parts) >= 4:
                permissions = parts[0]
                owner = parts[2]
                group = parts[3]

                # Check if permissions are secure
                is_secure = True
                message = (
                    f"File {file_path}: {permissions} (owner: {owner}, group: {group})"
                )

                # For /etc/shadow, should be 600 or 640
                if "shadow" in file_path:
                    if not permissions.endswith("------") and not permissions.endswith(
                        "----"
                    ):
                        is_secure = False
                        message += " - WARNING: Shadow file permissions too permissive!"

                points = 10 if is_secure else 5
                status = (
                    ValidationStatus.PASSED if is_secure else ValidationStatus.FAILED
                )

                return self.create_check(
                    f"file_{file_path.replace('/', '_')}",
                    f"File {file_path} permissions",
                    status,
                    message,
                    points,
                    10,
                )

            return self.create_check(
                f"file_{file_path.replace('/', '_')}",
                f"File {file_path}",
                ValidationStatus.ERROR,
                f"Could not parse permissions for {file_path}",
                0,
                10,
            )

        except Exception as e:
            return self.create_check(
                f"file_{file_path.replace('/', '_')}",
                f"File {file_path}",
                ValidationStatus.ERROR,
                f"Error checking {file_path}: {str(e)}",
                0,
                10,
            )

    async def _execute_check(
        self, command: str, context: ValidationContext
    ) -> Dict[str, Any]:
        """Execute a check in container"""
        return await self.docker_client.exec_command(context.container_id, command)
