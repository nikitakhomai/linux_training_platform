"""Analytics endpoints"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

from app.services.statistics import StatisticsService
from app.api.dependencies import get_statistics_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/tasks/{task_id}/stats")
async def get_task_statistics(
    task_id: int, stats: StatisticsService = Depends(get_statistics_service)
):
    """Get statistics for a specific task"""
    task_stats = await stats.get_task_statistics(task_id)
    return task_stats


@router.get("/overall")
async def get_overall_statistics(
    stats: StatisticsService = Depends(get_statistics_service),
):
    """Get overall platform statistics"""
    overall_stats = await stats.get_overall_statistics()
    return overall_stats


@router.get("/skills/distribution")
async def get_skills_distribution(
    stats: StatisticsService = Depends(get_statistics_service),
):
    """Get skills distribution across all users"""
    distribution = await stats.get_skills_distribution()
    return distribution
