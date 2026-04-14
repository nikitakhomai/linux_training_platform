"""API dependencies - Simplified version without JWT for testing"""

from fastapi import HTTPException, status, Header
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
) -> dict:
    """
    Get current user from headers (simplified for testing)
    In production, this should validate JWT token
    """
    # For testing, allow any user
    if not x_user_id:
        # Default user for testing
        return {"id": 1, "username": "testuser", "role": "student"}

    return {
        "id": int(x_user_id),
        "username": f"user_{x_user_id}",
        "role": x_user_role or "student",
    }


async def get_container_manager():
    """Get container manager instance"""
    from app.services.container_manager import ContainerManager

    manager = ContainerManager()
    await manager.start()
    return manager
