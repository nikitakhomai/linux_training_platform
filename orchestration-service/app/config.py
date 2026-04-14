"""Configuration management"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Service configuration
    SERVICE_NAME: str = "orchestration-service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = "0.0.0.0"
    PORT: int = 8003

    # Kubernetes configuration
    KUBERNETES_MODE: bool = Field(default=False)
    KUBERNETES_NAMESPACE_PREFIX: str = "student-"

    # Docker configuration (fallback)
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    DOCKER_NETWORK: str = "training-network"

    # Container defaults
    DEFAULT_IMAGE: str = "ubuntu:22.04"
    DEFAULT_MEMORY_LIMIT: str = "512Mi"
    DEFAULT_CPU_LIMIT: str = "500m"
    DEFAULT_TIMEOUT_SECONDS: int = 3600

    # Resource quotas
    MAX_CONTAINERS_PER_USER: int = 3

    # Security (optional for development)
    JWT_SECRET_KEY: str = Field(default="dev-secret-key-for-testing-only")
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = Field(default=["*"])

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


settings = Settings()
