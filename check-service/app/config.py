"""Configuration management"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    SERVICE_NAME: str = "check-service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = "0.0.0.0"
    PORT: int = 8002

    # Redis configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Task Service integration
    TASK_SERVICE_URL: str = Field(default="http://localhost:8001")

    # Docker configuration
    DOCKER_TIMEOUT: int = 300

    # Security
    JWT_SECRET_KEY: str = Field(default="dev-secret-key")
    JWT_ALGORITHM: str = "HS256"

    # CORS - простая строка
    CORS_ORIGINS: str = Field(default="*")

    # Validation settings
    VALIDATION_TIMEOUT: int = 60

    # Logging
    LOG_LEVEL: str = Field(default="INFO")


settings = Settings()
