from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from src.models.course import Course
from src.schemas.course import CourseCreate, CourseUpdate

class CRUDCourse:
    async def get(self, db: AsyncSession, course_id: int) -> Optional[Course]:
        """Получить курс по ID"""
        result = await db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[int] = None,
        is_published: Optional[bool] = None
    ) -> List[Course]:
        """Получить список курсов"""
        query = select(Course)
        
        if category_id is not None:
            query = query.where(Course.category_id == category_id)
        
        if is_published is not None:
            query = query.where(Course.is_published == is_published)
        
        query = query.offset(skip).limit(limit).order_by(Course.order)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, course_in: CourseCreate) -> Course:
        """Создать новый курс"""
        db_course = Course(**course_in.model_dump())
        db.add(db_course)
        await db.commit()
        await db.refresh(db_course)
        return db_course
    
    async def update(self, db: AsyncSession, course_id: int, course_in: CourseUpdate) -> Optional[Course]:
        """Обновить курс"""
        update_data = course_in.model_dump(exclude_unset=True)
        
        if not update_data:
            return await self.get(db, course_id)
        
        stmt = update(Course).where(Course.id == course_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        
        return await self.get(db, course_id)
    
    async def delete(self, db: AsyncSession, course_id: int) -> bool:
        """Удалить курс"""
        stmt = delete(Course).where(Course.id == course_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

crud_course = CRUDCourse()
