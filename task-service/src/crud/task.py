from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate

class CRUDTask:
    async def get(self, db: AsyncSession, task_id: int) -> Optional[Task]:
        """Получить задание по ID"""
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        course_id: Optional[int] = None,
        is_published: Optional[bool] = None
    ) -> List[Task]:
        """Получить список заданий"""
        query = select(Task)
        
        if course_id is not None:
            query = query.where(Task.course_id == course_id)
        
        if is_published is not None:
            query = query.where(Task.is_published == is_published)
        
        query = query.offset(skip).limit(limit).order_by(Task.order_in_course)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, task_in: TaskCreate) -> Task:
        """Создать новое задание"""
        db_task = Task(**task_in.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    async def update(self, db: AsyncSession, task_id: int, task_in: TaskUpdate) -> Optional[Task]:
        """Обновить задание"""
        update_data = task_in.model_dump(exclude_unset=True)
        
        if not update_data:
            return await self.get(db, task_id)
        
        stmt = update(Task).where(Task.id == task_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        
        return await self.get(db, task_id)
    
    async def delete(self, db: AsyncSession, task_id: int) -> bool:
        """Удалить задание"""
        stmt = delete(Task).where(Task.id == task_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

crud_task = CRUDTask()
