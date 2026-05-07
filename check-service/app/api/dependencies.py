from fastapi import HTTPException, status, Header
from typing import Optional
import logging

from app.services.validator import ValidationService

logger = logging.getLogger(__name__)


async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
) -> dict:
    if not x_user_id:
        return {"id": 1, "username": "testuser", "role": "student"}
    return {
        "id": int(x_user_id),
        "username": f"user_{x_user_id}",
        "role": x_user_role or "student",
    }


async def get_validation_service():
    """Создает новый экземпляр валидационного сервиса"""
    return ValidationService()
