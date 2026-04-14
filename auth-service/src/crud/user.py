from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash

class CRUDUser:
    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, user_in: UserCreate) -> User:
        """Создать нового пользователя"""
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=hashed_password,
            role=user_in.role
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    async def update(self, db: AsyncSession, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        update_data = user_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        stmt = update(User).where(User.id == user_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        
        return await self.get_by_id(db, user_id)
    
    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not user.is_active:
            return None
        
        from src.core.security import verify_password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user

crud_user = CRUDUser()
