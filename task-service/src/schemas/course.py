from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.schemas.task import TaskResponse


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty: str = Field(
        default="beginner", pattern="^(beginner|intermediate|advanced)$"
    )
    category_id: Optional[int] = None
    order: int = Field(default=0, ge=0)
    is_published: bool = Field(default=False)
    estimated_time_minutes: int = Field(default=60, ge=1)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty: Optional[str] = Field(
        None, pattern="^(beginner|intermediate|advanced)$"
    )
    category_id: Optional[int] = None
    order: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None
    estimated_time_minutes: Optional[int] = Field(None, ge=1)


class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True
        # Временно убираем проверку типов для асинхронной загрузки
        arbitrary_types_allowed = True
