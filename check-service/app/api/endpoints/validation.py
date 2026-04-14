"""Validation API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import uuid
from datetime import datetime
import logging

from app.models.schemas import (
    ValidationRequest,
    ValidationResponse,
    ValidationStatus,
    ValidationErrorResponse,
)
from app.services.validator import ValidationService
from app.api.dependencies import get_validation_service, get_current_user
from app.core.exceptions import ValidationError, ContainerError


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/validate",
    response_model=ValidationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ValidationErrorResponse},
        404: {"model": ValidationErrorResponse},
        503: {"model": ValidationErrorResponse},
    },
)
async def validate_task(
    request: ValidationRequest,
    validation_service: ValidationService = Depends(get_validation_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Validate a task solution

    Executes validation checks against a container and returns detailed results
    """
    logger.info(
        f"Validation request for task {request.task_id} by user {request.user_id}"
    )

    # Verify user matches token
    if current_user["id"] != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User ID mismatch"
        )

    try:
        # Execute validation
        result = await validation_service.validate(request)

        return result

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ContainerError as e:
        logger.error(f"Container error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Container error: {e}",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/types")
async def get_validation_types():
    """Get available validation types"""
    return {
        "validation_types": [
            {
                "id": "ssh_config",
                "name": "SSH Configuration",
                "description": "Validate SSH security settings",
            },
            {
                "id": "file_permissions",
                "name": "File Permissions",
                "description": "Check file and directory permissions",
            },
            {
                "id": "firewall_rules",
                "name": "Firewall Rules",
                "description": "Validate firewall configuration",
            },
            {
                "id": "selinux",
                "name": "SELinux",
                "description": "Check SELinux status and policies",
            },
            {
                "id": "apparmor",
                "name": "AppArmor",
                "description": "Validate AppArmor profiles",
            },
            {
                "id": "audit_rules",
                "name": "Audit Rules",
                "description": "Check auditd configuration",
            },
            {
                "id": "user_accounts",
                "name": "User Accounts",
                "description": "Validate user account security",
            },
            {
                "id": "kernel_params",
                "name": "Kernel Parameters",
                "description": "Check kernel security parameters",
            },
            {
                "id": "systemd_services",
                "name": "Systemd Services",
                "description": "Validate service configurations",
            },
            {
                "id": "package_management",
                "name": "Package Management",
                "description": "Check package security",
            },
        ]
    }


@router.get("/task/{task_id}/requirements")
async def get_task_requirements(
    task_id: int,
    validation_service: ValidationService = Depends(get_validation_service),
):
    """Get validation requirements for a specific task"""
    try:
        requirements = await validation_service.get_task_validation_requirements(
            task_id
        )
        return requirements
    except Exception as e:
        logger.error(f"Error getting task requirements: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found"
        )
