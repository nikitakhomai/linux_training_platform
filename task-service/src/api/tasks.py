from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.core.database import get_db
from src.core.security import get_current_user, get_current_admin_user
from src.crud.task import crud_task
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.get("/public", response_model=List[TaskResponse])
async def read_public_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    course_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint - no authentication required"""
    tasks = await crud_task.get_multi(
        db, skip=skip, limit=limit, course_id=course_id, is_published=True
    )
    return tasks


@router.get("/public/courses", response_model=List[dict])
async def read_public_courses(
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint - get all courses"""
    from src.crud.course import crud_course

    courses = await crud_course.get_multi(db, is_published=True)
    return courses


@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    course_id: Optional[int] = Query(None),
    is_published: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tasks = await crud_task.get_multi(
        db, skip=skip, limit=limit, course_id=course_id, is_published=is_published
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = await crud_task.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    body = await request.json()
    print(f"CREATE TASK RAW: {body}")
    task_data = TaskCreate(**body)
    task = await crud_task.create(db, task_data)
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    body = await request.json()
    print(f"UPDATE TASK RAW: {body}")
    task_data = TaskUpdate(**body)
    updated = await crud_task.update(db, task_id, task_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    success = await crud_task.delete(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
