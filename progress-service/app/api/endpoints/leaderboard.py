"""Leaderboard endpoints"""

from fastapi import APIRouter, Depends
from typing import List
import logging

from app.models.schemas import LeaderboardEntry
from app.services.statistics import StatisticsService
from app.api.dependencies import get_statistics_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 10, stats: StatisticsService = Depends(get_statistics_service)
):
    """Get top users by score"""
    leaderboard = await stats.get_leaderboard(limit)
    return leaderboard


@router.get("/user/{user_id}/rank", response_model=dict)
async def get_user_rank(
    user_id: int, stats: StatisticsService = Depends(get_statistics_service)
):
    """Get user rank"""
    rank = await stats.get_user_rank(user_id)
    return {"user_id": user_id, "rank": rank}
