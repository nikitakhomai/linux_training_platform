from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Сложность курса
    difficulty = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    
    # Принадлежность к категории
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", backref="courses")
    
    # Порядок и видимость
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    
    # Ожидаемое время выполнения
    estimated_time_minutes = Column(Integer, default=60)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Course {self.title}>"
