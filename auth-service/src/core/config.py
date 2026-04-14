from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str = "Auth Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # JWT настройки
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Настройки базы данных
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/auth_db"

    # Redis для токенов
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://frontend:3000"]

    # ✅ ДОБАВЬТЕ ЭТУ КОНФИГУРАЦИЮ
    class Config:
        extra = "ignore"  # Игнорировать лишние поля из .env
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
