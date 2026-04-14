from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str = "Task Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # База данных
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@postgres:5432/task_db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/1"
    
    # Auth Service URL для проверки токенов
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    
    # JWT настройки (должны совпадать с auth-service)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://frontend:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
