from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from src.models.category import Category
from src.schemas.category import CategoryCreate, CategoryUpdate

class CRUDCategory:
    async def get(self, db: AsyncSession, category_id: int) -> Optional[Category]:
        """Получить категорию по ID"""
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """Получить список категорий"""
        result = await db.execute(
            select(Category).offset(skip).limit(limit).order_by(Category.name)
        )
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, category_in: CategoryCreate) -> Category:
        """Создать новую категорию"""
        db_category = Category(**category_in.model_dump())
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category
    
    async def update(self, db: AsyncSession, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
        """Обновить категорию"""
        update_data = category_in.model_dump(exclude_unset=True)
        
        if not update_data:
            return await self.get(db, category_id)
        
        stmt = update(Category).where(Category.id == category_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        
        return await self.get(db, category_id)
    
    async def delete(self, db: AsyncSession, category_id: int) -> bool:
        """Удалить категорию"""
        stmt = delete(Category).where(Category.id == category_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

crud_category = CRUDCategory()
