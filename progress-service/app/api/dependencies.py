"""API dependencies"""

from fastapi import HTTPException, status, Header
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

# Глобальный экземпляр ProgressTracker (синглтон)
_progress_tracker = None
_statistics_service = None


async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
) -> dict:
    """Get current user from headers"""
    user_id = int(x_user_id) if x_user_id else 1
    return {
        "id": user_id,
        "username": f"user_{user_id}",
        "role": x_user_role or "admin",
    }


async def get_progress_tracker():
    """Get progress tracker instance (singleton)"""
    global _progress_tracker
    if _progress_tracker is None:
        from app.services.progress_tracker import ProgressTracker

        _progress_tracker = ProgressTracker()
        logger.info("Created new ProgressTracker instance")
    return _progress_tracker


async def get_statistics_service():
    """Get statistics service instance (singleton)"""
    global _statistics_service
    if _statistics_service is None:
        from app.services.statistics import StatisticsService

        tracker = await get_progress_tracker()
        _statistics_service = StatisticsService(tracker)
        logger.info("Created new StatisticsService instance")
    return _statistics_service
