"""Configuration management for Check Service"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Service configuration
    SERVICE_NAME: str = "check-service"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = "0.0.0.0"
    PORT: int = 8002

    # Redis configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = 10

    # Task Service integration
    TASK_SERVICE_URL: str = Field(default="http://localhost:8001")
    TASK_SERVICE_TIMEOUT: int = 30

    # Docker configuration
    DOCKER_TIMEOUT: int = 300
    DOCKER_MEMORY_LIMIT: str = "512m"
    DOCKER_CPU_LIMIT: float = 1.0

    # Security
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-min-32-chars-long"
    )
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    # Validation settings
    VALIDATION_TIMEOUT: int = 60
    MAX_VALIDATION_RETRIES: int = 3

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
