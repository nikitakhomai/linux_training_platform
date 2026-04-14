from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base
import enum

class TaskType(str, enum.Enum):
    HARDENING = "hardening"        # Харденинг системы
    AUDIT = "audit"                # Аудит безопасности
    PENETRATION = "penetration"    # Тестирование на проникновение
    CONFIGURATION = "configuration" # Конфигурация
    MONITORING = "monitoring"      # Мониторинг

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Тип задания
    task_type = Column(String(50), default=TaskType.HARDENING.value)
    
    # Принадлежность к курсу
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    course = relationship("Course", backref="tasks")
    
    # Порядок в курсе
    order_in_course = Column(Integer, default=0)
    
    # Docker образ для задания
    docker_image = Column(String(255), nullable=False)
    docker_command = Column(String(255), nullable=True)
    
    # Конфигурация задания
    config = Column(JSON, nullable=True)  # Дополнительные настройки
    
    # Проверочные скрипты
    validation_script = Column(Text, nullable=True)
    hint_script = Column(Text, nullable=True)
    
    # Сложность
    points = Column(Integer, default=10)  # Очки за выполнение
    difficulty = Column(String(20), default="easy")  # easy, medium, hard
    
    # Время
    estimated_time_minutes = Column(Integer, default=15)
    
    # Флаги
    is_published = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)  # Шаблон для создания заданий
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Task {self.title}>"
