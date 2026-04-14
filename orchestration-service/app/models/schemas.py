"""Pydantic schemas for Orchestration Service"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ContainerStatus(str, Enum):
    """Container status"""

    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DELETED = "deleted"
    TIMEOUT = "timeout"


class NamespaceStatus(str, Enum):
    """Namespace status"""

    ACTIVE = "active"
    TERMINATING = "terminating"
    ERROR = "error"


class ContainerRequest(BaseModel):
    """Request to create a container"""

    task_id: int = Field(..., gt=0, description="Task ID")
    user_id: int = Field(..., gt=0, description="User ID")
    docker_image: str = Field(default="ubuntu:22.04", description="Docker image to use")
    memory_limit: str = Field(default="512Mi", description="Memory limit")
    cpu_limit: str = Field(default="500m", description="CPU limit")
    timeout_seconds: int = Field(
        default=3600, description="Container lifetime in seconds"
    )

    @field_validator("docker_image")
    @classmethod
    def validate_image(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Invalid docker image")
        return v


class ContainerResponse(BaseModel):
    """Container information"""

    container_id: str
    task_id: int
    user_id: int
    name: str
    namespace: str
    status: ContainerStatus
    image: str
    created_at: datetime
    expires_at: datetime
    last_accessed: Optional[datetime] = None
    connection_details: Dict[str, Any]
    error_message: Optional[str] = None


class ContainerListResponse(BaseModel):
    """List of containers for user"""

    containers: List[ContainerResponse]
    total: int
    active: int


class NamespaceRequest(BaseModel):
    """Request to create a namespace"""

    user_id: int
    username: str
    resource_quotas: Optional[Dict[str, str]] = None


class NamespaceResponse(BaseModel):
    """Namespace information"""

    namespace: str
    user_id: int
    username: str
    status: NamespaceStatus
    created_at: datetime
    containers_count: int
    resource_usage: Dict[str, Any]


class ContainerAction(BaseModel):
    """Action to perform on container"""

    action: str = Field(..., pattern="^(start|stop|restart|delete)$")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        valid_actions = ["start", "stop", "restart", "delete"]
        if v not in valid_actions:
            raise ValueError(f"Action must be one of: {valid_actions}")
        return v


class ContainerMetrics(BaseModel):
    """Container metrics"""

    container_id: str
    cpu_usage: float
    memory_usage: int
    memory_limit: int
    network_rx: int
    network_tx: int
    uptime_seconds: int
    timestamp: datetime


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: str
    timestamp: datetime
    kubernetes_available: bool
    docker_available: bool
    details: Dict[str, Any]
