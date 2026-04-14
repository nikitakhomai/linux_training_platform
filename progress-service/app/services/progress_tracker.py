"""Progress tracking service"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from app.models.schemas import (
    TaskSubmission,
    TaskProgress,
    CourseProgress,
    SkillScore,
    UserProgress,
    ProgressSummary,
    TaskStatus,
    SkillCategory,
    SkillLevel,
)

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track user progress"""

    def __init__(self):
        # Хранилище данных
        self.submissions: Dict[int, List[TaskSubmission]] = defaultdict(list)
        # user_progress: user_id -> {task_id: {best_score, attempts, ...}}
        self.user_progress: Dict[int, Dict[int, Dict]] = defaultdict(
            lambda: defaultdict(dict)
        )
        self.streaks: Dict[int, Dict] = defaultdict(
            lambda: {"current": 0, "best": 0, "last": None}
        )

        # Mock tasks data
        self.tasks = {
            1: {
                "id": 1,
                "name": "SSH Hardening",
                "category": SkillCategory.SSH,
                "max_score": 100,
            },
            2: {
                "id": 2,
                "name": "File Permissions",
                "category": SkillCategory.PERMISSIONS,
                "max_score": 100,
            },
            3: {
                "id": 3,
                "name": "Firewall Configuration",
                "category": SkillCategory.FIREWALL,
                "max_score": 100,
            },
            4: {
                "id": 4,
                "name": "SELinux Policies",
                "category": SkillCategory.SELINUX,
                "max_score": 100,
            },
            5: {
                "id": 5,
                "name": "Audit Rules",
                "category": SkillCategory.AUDIT,
                "max_score": 100,
            },
        }

        self.courses = {
            1: {"id": 1, "name": "Linux Security Basics", "tasks": [1, 2]},
            2: {"id": 2, "name": "Advanced Security", "tasks": [3, 4, 5]},
        }

        logger.info("ProgressTracker initialized")

    async def submit_task(self, submission: TaskSubmission) -> Dict:
        """Record task submission"""
        user_id = submission.user_id
        task_id = submission.task_id

        logger.info(
            f"Recording submission for user {user_id}, task {task_id}, score={submission.score}, passed={submission.passed}"
        )

        # Store submission
        self.submissions[user_id].append(submission)

        # Get current progress for this task
        task_progress = self.user_progress[user_id].get(
            task_id,
            {
                "best_score": 0.0,
                "attempts": 0,
                "status": TaskStatus.NOT_STARTED,
                "completed_at": None,
                "last_attempt": None,
                "last_score": 0.0,
            },
        )

        # Update best score if current submission is better
        if submission.score > task_progress["best_score"]:
            task_progress["best_score"] = submission.score
            task_progress["status"] = (
                TaskStatus.COMPLETED if submission.passed else TaskStatus.FAILED
            )
            if submission.passed:
                task_progress["completed_at"] = datetime.utcnow()
            logger.info(
                f"New best score for user {user_id}, task {task_id}: {submission.score}"
            )

        # Update attempts
        task_progress["attempts"] += 1
        task_progress["last_attempt"] = datetime.utcnow()
        task_progress["last_score"] = submission.score

        # Save back
        self.user_progress[user_id][task_id] = task_progress

        logger.info(
            f"User {user_id}, task {task_id}: best_score={task_progress['best_score']}, attempts={task_progress['attempts']}"
        )

        # Update streak if passed
        if submission.passed:
            await self._update_streak(user_id)

        return {
            "recorded": True,
            "user_id": user_id,
            "task_id": task_id,
            "best_score": task_progress["best_score"],
            "attempts": task_progress["attempts"],
        }

    async def _update_streak(self, user_id: int):
        """Update user streak"""
        now = datetime.utcnow().date()
        streak_data = self.streaks[user_id]
        last = streak_data.get("last")

        if last:
            last_date = last.date() if isinstance(last, datetime) else last
            if (now - last_date).days == 1:
                streak_data["current"] += 1
            elif (now - last_date).days > 1:
                streak_data["current"] = 1
        else:
            streak_data["current"] = 1

        streak_data["last"] = now
        streak_data["best"] = max(streak_data["best"], streak_data["current"])

        logger.info(
            f"User {user_id} streak: current={streak_data['current']}, best={streak_data['best']}"
        )

    async def get_user_progress(
        self, user_id: int, username: str = "user"
    ) -> UserProgress:
        """Get complete user progress"""
        logger.info(f"Getting progress for user {user_id}")

        # Calculate courses progress
        courses_progress = []
        for course_id, course in self.courses.items():
            completed = 0
            total_score = 0
            tasks_progress = []

            for task_id in course["tasks"]:
                task_data = self.user_progress[user_id].get(task_id, {})
                task_info = self.tasks.get(task_id, {})

                best_score = task_data.get("best_score", 0)
                attempts = task_data.get("attempts", 0)

                # Determine status
                if best_score >= 70:
                    status = TaskStatus.COMPLETED
                elif attempts > 0:
                    status = TaskStatus.FAILED
                else:
                    status = TaskStatus.NOT_STARTED

                task_progress = TaskProgress(
                    task_id=task_id,
                    task_name=task_info.get("name", f"Task {task_id}"),
                    status=status,
                    score=best_score,
                    attempts=attempts,
                    best_score=best_score,
                    completed_at=task_data.get("completed_at"),
                    last_attempt=task_data.get("last_attempt", datetime.utcnow()),
                )
                tasks_progress.append(task_progress)

                if best_score >= 70:
                    completed += 1
                    total_score += best_score

            percentage = (
                (completed / len(course["tasks"])) * 100 if course["tasks"] else 0
            )
            courses_progress.append(
                CourseProgress(
                    course_id=course_id,
                    course_name=course["name"],
                    total_tasks=len(course["tasks"]),
                    completed_tasks=completed,
                    percentage=percentage,
                    total_score=total_score,
                    tasks=tasks_progress,
                )
            )

        # Calculate skills
        skills = []
        for category in SkillCategory:
            category_tasks = [
                t for t in self.tasks.values() if t["category"] == category
            ]
            if not category_tasks:
                continue

            completed = 0
            total_score = 0
            for task in category_tasks:
                task_id = task["id"]
                task_data = self.user_progress[user_id].get(task_id, {})
                score = task_data.get("best_score", 0)
                if score >= 70:
                    completed += 1
                total_score += score

            avg_score = (total_score / len(category_tasks)) if category_tasks else 0
            level = self._get_skill_level(avg_score, completed, len(category_tasks))

            skills.append(
                SkillScore(
                    category=category,
                    score=avg_score,
                    level=level,
                    tasks_completed=completed,
                    total_tasks=len(category_tasks),
                )
            )

        # Generate recommendations
        recommendations = await self._generate_recommendations(user_id)

        # Calculate total score
        total_score = sum(s.score for s in skills) / len(skills) if skills else 0

        return UserProgress(
            user_id=user_id,
            username=username,
            total_score=total_score,
            courses_progress=courses_progress,
            skills=skills,
            achievements=[],
            recommendations=recommendations,
        )

    def _get_skill_level(self, score: float, completed: int, total: int) -> SkillLevel:
        """Determine skill level based on score and completion"""
        if completed == total and score >= 90:
            return SkillLevel.EXPERT
        elif score >= 80:
            return SkillLevel.ADVANCED
        elif score >= 60:
            return SkillLevel.INTERMEDIATE
        else:
            return SkillLevel.BEGINNER

    async def _generate_recommendations(self, user_id: int) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        progress = self.user_progress[user_id]

        # Find weak skills
        for category in SkillCategory:
            category_tasks = [
                t for t in self.tasks.values() if t["category"] == category
            ]
            completed = 0
            for task in category_tasks:
                task_data = progress.get(task["id"], {})
                if task_data.get("best_score", 0) >= 70:
                    completed += 1

            if completed < len(category_tasks):
                recommendations.append(
                    f"Practice more in {category.value.upper()} security"
                )

        # Add general recommendations
        if not recommendations:
            recommendations.append(
                "Great job! Try advanced tasks to improve your skills"
            )

        return recommendations[:3]

    async def get_progress_summary(self, user_id: int) -> ProgressSummary:
        """Get progress summary for dashboard"""
        progress = await self.get_user_progress(user_id, "user")

        total_completed = sum(c.completed_tasks for c in progress.courses_progress)
        total_courses = sum(1 for c in progress.courses_progress if c.percentage == 100)
        avg_score = progress.total_score

        streak_data = self.streaks[user_id]

        return ProgressSummary(
            user_id=user_id,
            total_tasks_completed=total_completed,
            total_courses_completed=total_courses,
            average_score=avg_score,
            current_streak=streak_data["current"],
            best_streak=streak_data["best"],
            total_points=int(avg_score * 10),
            rank=1,
            next_achievement={
                "name": "Security Expert",
                "description": "Complete all tasks with 90%+ score",
                "progress": f"{total_completed}/{len(self.tasks)}",
            },
        )
