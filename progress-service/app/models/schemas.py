"""Pydantic schemas for Progress Service"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SkillLevel(str, Enum):
    """Skill level"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TaskStatus(str, Enum):
    """Task completion status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SkillCategory(str, Enum):
    """Skill categories"""

    SSH = "ssh"
    PERMISSIONS = "permissions"
    FIREWALL = "firewall"
    SELINUX = "selinux"
    AUDIT = "audit"
    KERNEL = "kernel"


class TaskSubmission(BaseModel):
    """Task submission data"""

    task_id: int
    user_id: int
    score: float = Field(..., ge=0, le=100)
    passed: bool
    details: Optional[Dict[str, Any]] = None


class TaskProgress(BaseModel):
    """Task progress for a user"""

    task_id: int
    task_name: str
    status: TaskStatus
    score: float
    attempts: int
    best_score: float
    completed_at: Optional[datetime]
    last_attempt: datetime


class CourseProgress(BaseModel):
    """Course progress for a user"""

    course_id: int
    course_name: str
    total_tasks: int
    completed_tasks: int
    percentage: float
    total_score: float
    tasks: List[TaskProgress]


class SkillScore(BaseModel):
    """Score for a skill category"""

    category: SkillCategory
    score: float = Field(..., ge=0, le=100)
    level: SkillLevel
    tasks_completed: int
    total_tasks: int


class UserProgress(BaseModel):
    """Complete user progress"""

    user_id: int
    username: str
    total_score: float
    courses_progress: List[CourseProgress]
    skills: List[SkillScore]
    achievements: List[Dict[str, Any]]
    recommendations: List[str]


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""

    user_id: int
    username: str
    total_score: float
    tasks_completed: int
    rank: int


class Achievement(BaseModel):
    """User achievement"""

    id: str
    name: str
    description: str
    icon: str
    unlocked_at: datetime


class ProgressSummary(BaseModel):
    """Progress summary for dashboard"""

    user_id: int
    total_tasks_completed: int
    total_courses_completed: int
    average_score: float
    current_streak: int
    best_streak: int
    total_points: int
    rank: int
    next_achievement: Optional[Dict[str, Any]]
