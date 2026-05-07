from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.core.database import get_db
from src.core.security import get_current_user, get_current_admin_user
from src.crud.course import crud_course
from src.schemas.course import CourseCreate, CourseUpdate, CourseResponse

router = APIRouter()

# ============================================
# ПУБЛИЧНЫЕ ЭНДПОИНТЫ (без авторизации) - ДОЛЖНЫ БЫТЬ ПЕРВЫМИ!
# ============================================


@router.get("/public", response_model=List[CourseResponse])
async def get_public_courses(
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint - get all published courses (no auth required)"""
    courses = await crud_course.get_multi(db, is_published=True)
    return courses


# ============================================
# ЗАЩИЩЕННЫЕ ЭНДПОИНТЫ
# ============================================


@router.get("/", response_model=List[CourseResponse])
async def read_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    is_published: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    courses = await crud_course.get_multi(
        db, skip=skip, limit=limit, category_id=category_id, is_published=is_published
    )
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def read_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    course = await crud_course.get(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=CourseResponse)
async def create_course(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    body = await request.json()
    print(f"\n🎯🎯🎯 RAW REQUEST BODY: {body}")
    course_data = CourseCreate(**body)
    course = await crud_course.create(db, course_data)
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course: CourseUpdate = Body(..., embed=False),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    print(f"UPDATE COURSE {course_id}: {course}")
    updated = await crud_course.update(db, course_id, course)
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    success = await crud_course.delete(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}
