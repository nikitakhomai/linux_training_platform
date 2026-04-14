from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    task_type: str = Field(default="hardening")
    course_id: Optional[int] = None
    order_in_course: int = Field(default=0, ge=0)
    docker_image: str = Field(..., min_length=1)
    docker_command: Optional[str] = None
    config: Optional[dict] = None
    validation_script: Optional[str] = None
    hint_script: Optional[str] = None
    points: int = Field(default=10, ge=1)
    difficulty: str = Field(default="easy", pattern="^(easy|medium|hard)$")
    estimated_time_minutes: int = Field(default=15, ge=1)
    is_published: bool = Field(default=False)
    is_template: bool = Field(default=False)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    task_type: Optional[str] = None
    course_id: Optional[int] = None
    order_in_course: Optional[int] = Field(None, ge=0)
    docker_image: Optional[str] = Field(None, min_length=1)
    docker_command: Optional[str] = None
    config: Optional[dict] = None
    validation_script: Optional[str] = None
    hint_script: Optional[str] = None
    points: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    estimated_time_minutes: Optional[int] = Field(None, ge=1)
    is_published: Optional[bool] = None
    is_template: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
