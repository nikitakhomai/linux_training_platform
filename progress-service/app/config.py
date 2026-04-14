"""Configuration management"""

from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import json


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    SERVICE_NAME: str = "progress-service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = "0.0.0.0"
    PORT: int = 8004

    # Services
    TASK_SERVICE_URL: str = Field(default="http://localhost:8001")
    CHECK_SERVICE_URL: str = Field(default="http://localhost:8002")

    # JWT
    JWT_SECRET_KEY: str = Field(default="dev-secret-key")
    JWT_ALGORITHM: str = "HS256"

    # CORS - используем простую строку, а не список
    CORS_ORIGINS_STR: str = Field(default="*", alias="CORS_ORIGINS")
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from string"""
        if self.CORS_ORIGINS_STR == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]


settings = Settings()
