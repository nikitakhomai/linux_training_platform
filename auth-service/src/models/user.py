from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from src.core.base import Base  # Импортируем Base из отдельного файла
import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)

    # Хэш пароля
    hashed_password = Column(String, nullable=False)

    # Роль пользователя
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)

    # Активен ли пользователь
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Даты
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
