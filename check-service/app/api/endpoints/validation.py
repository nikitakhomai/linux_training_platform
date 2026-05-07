from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from app.models.schemas import ValidationRequest, ValidationResponse
from app.services.validator import ValidationService
from app.api.dependencies import get_validation_service, get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/validate", response_model=ValidationResponse)
async def validate_task(
    request: ValidationRequest,
    validation_service: ValidationService = Depends(get_validation_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    logger.info(f"Validation request for task {request.task_id}")

    # if current_user["id"] != request.user_id:
    #     raise HTTPException(status_code=403, detail="User ID mismatch")

    # Вызываем реальную валидацию
    result = await validation_service.validate(request)
    return result


@router.get("/types")
async def get_validation_types():
    return {
        "validation_types": [
            {
                "id": "ssh_config",
                "name": "SSH Configuration",
                "description": "Validate SSH security settings",
            },
        ]
    }
