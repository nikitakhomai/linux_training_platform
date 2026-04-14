"""Progress tracking endpoints"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from app.models.schemas import TaskSubmission, UserProgress, ProgressSummary
from app.services.progress_tracker import ProgressTracker
from app.api.dependencies import get_progress_tracker, get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submit", response_model=dict)
async def submit_task(
    submission: TaskSubmission,
    tracker: ProgressTracker = Depends(get_progress_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Submit task completion"""
    if current_user["id"] != submission.user_id:
        raise HTTPException(status_code=403, detail="Cannot submit for another user")

    result = await tracker.submit_task(submission)
    return result


@router.get("/user/{user_id}", response_model=UserProgress)
async def get_user_progress(
    user_id: int,
    tracker: ProgressTracker = Depends(get_progress_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Get user progress"""
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    progress = await tracker.get_user_progress(
        user_id, current_user.get("username", "user")
    )
    return progress


@router.get("/summary", response_model=ProgressSummary)
async def get_progress_summary(
    tracker: ProgressTracker = Depends(get_progress_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Get progress summary for current user"""
    summary = await tracker.get_progress_summary(current_user["id"])
    return summary
