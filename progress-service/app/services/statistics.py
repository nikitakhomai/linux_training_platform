"""Statistics service"""

from typing import List, Dict, Any
import logging

from app.models.schemas import LeaderboardEntry

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for platform statistics"""

    def __init__(self, progress_tracker):
        self.progress_tracker = progress_tracker

    async def get_leaderboard(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top users by score"""
        # Mock data for now
        return [
            LeaderboardEntry(
                user_id=1, username="alice", total_score=95.5, tasks_completed=8, rank=1
            ),
            LeaderboardEntry(
                user_id=2, username="bob", total_score=87.3, tasks_completed=7, rank=2
            ),
            LeaderboardEntry(
                user_id=3,
                username="charlie",
                total_score=76.8,
                tasks_completed=6,
                rank=3,
            ),
        ][:limit]

    async def get_user_rank(self, user_id: int) -> int:
        """Get user rank"""
        leaderboard = await self.get_leaderboard(100)
        for i, entry in enumerate(leaderboard, 1):
            if entry.user_id == user_id:
                return i
        return len(leaderboard) + 1

    async def get_task_statistics(self, task_id: int) -> Dict[str, Any]:
        """Get statistics for a task"""
        return {
            "task_id": task_id,
            "total_attempts": 150,
            "successful_attempts": 120,
            "success_rate": 80.0,
            "average_score": 75.5,
            "average_time_minutes": 15,
        }

    async def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall platform statistics"""
        return {
            "total_users": 50,
            "total_tasks_completed": 450,
            "average_score": 72.5,
            "active_users_last_7d": 35,
            "most_popular_task": 1,
            "hardest_task": 3,
        }

    async def get_skills_distribution(self) -> Dict[str, Any]:
        """Get skills distribution"""
        return {
            "ssh": {"beginner": 20, "intermediate": 15, "advanced": 10, "expert": 5},
            "permissions": {
                "beginner": 18,
                "intermediate": 12,
                "advanced": 8,
                "expert": 2,
            },
            "firewall": {
                "beginner": 15,
                "intermediate": 10,
                "advanced": 5,
                "expert": 1,
            },
        }
