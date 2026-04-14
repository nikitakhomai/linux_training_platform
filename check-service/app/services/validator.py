"""Validation service orchestrator"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid

from app.models.schemas import (
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    ValidationStatus,
)
from app.services.docker_client import DockerClient
from app.validators.ssh_validator import SSHValidator
from app.validators.permissions_validator import PermissionsValidator
from app.validators.firewall_validator import FirewallValidator
from app.validators.base import ValidationContext

logger = logging.getLogger(__name__)


class ValidationService:
    """Main validation service orchestrator"""

    def __init__(self, docker_client: DockerClient = None):
        self.docker_client = docker_client or DockerClient()
        self.validators = {
            "ssh_config": SSHValidator(self.docker_client),
            "file_permissions": PermissionsValidator(self.docker_client),
            "firewall_rules": FirewallValidator(self.docker_client),
        }

    async def validate(self, request: ValidationRequest) -> ValidationResponse:
        """
        Execute validation for a task

        Args:
            request: Validation request with task and container info

        Returns:
            ValidationResponse with detailed results
        """
        start_time = datetime.utcnow()
        validation_id = str(uuid.uuid4())

        try:
            # Get validator for request type
            validator = self.validators.get(request.validation_type)
            if not validator:
                return self._create_error_response(
                    validation_id,
                    request,
                    start_time,
                    f"Unknown validation type: {request.validation_type}",
                )

            # Create validation context
            context = ValidationContext(
                container_id=request.container_id,
                task_id=request.task_id,
                user_id=request.user_id,
                validation_config={},
            )

            # Execute validation
            result = await validator.validate(context)

            # Create response
            return ValidationResponse(
                validation_id=validation_id,
                task_id=request.task_id,
                user_id=request.user_id,
                status=result.status,
                total_score=result.score,
                checks=result.checks,
                feedback=result.feedback,
                details=result.details,
                started_at=start_time,
                completed_at=datetime.utcnow(),
                duration_ms=int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                ),
            )

        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return self._create_error_response(
                validation_id, request, start_time, f"Validation failed: {str(e)}"
            )

    def _create_error_response(
        self,
        validation_id: str,
        request: ValidationRequest,
        start_time: datetime,
        error_message: str,
    ) -> ValidationResponse:
        """Create error response"""
        return ValidationResponse(
            validation_id=validation_id,
            task_id=request.task_id,
            user_id=request.user_id,
            status=ValidationStatus.ERROR,
            total_score=0.0,
            checks=[],
            feedback=f"Error during validation: {error_message}",
            details={"error": error_message},
            started_at=start_time,
            completed_at=datetime.utcnow(),
            duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
        )

    async def get_task_validation_requirements(self, task_id: int) -> Dict[str, Any]:
        """Get validation requirements for a task"""
        # This would normally fetch from Task Service
        return {
            "task_id": task_id,
            "validation_type": "ssh_config",
            "requirements": [
                "SSH Protocol must be version 2",
                "Root login must be disabled",
                "Password authentication must be disabled",
            ],
        }
