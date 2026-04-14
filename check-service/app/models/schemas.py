"""Pydantic schemas for Check Service"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ValidationStatus(str, Enum):
    """Validation result status"""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    PENDING = "pending"


class ValidationType(str, Enum):
    """Types of validations supported"""

    SSH_CONFIG = "ssh_config"
    FILE_PERMISSIONS = "file_permissions"
    FIREWALL_RULES = "firewall_rules"
    SELINUX = "selinux"
    APPARMOR = "apparmor"
    AUDIT_RULES = "audit_rules"
    USER_ACCOUNTS = "user_accounts"
    KERNEL_PARAMS = "kernel_params"
    SYSTEMD_SERVICES = "systemd_services"
    PACKAGE_MANAGEMENT = "package_management"


class ValidationCheck(BaseModel):
    """Individual validation check result"""

    check_id: str
    name: str
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    points: int = 0
    max_points: int = 10

    @property
    def score(self) -> float:
        """Calculate score for this check"""
        if self.max_points == 0:
            return 0.0
        return (self.points / self.max_points) * 100


class ValidationRequest(BaseModel):
    """Request to validate a task solution"""

    task_id: int = Field(..., gt=0, description="Task ID to validate")
    container_id: str = Field(
        ..., min_length=12, max_length=64, description="Docker container ID"
    )
    user_id: int = Field(..., gt=0, description="User ID submitting the validation")
    validation_type: ValidationType = Field(
        ..., description="Type of validation to perform"
    )

    @field_validator("container_id")
    @classmethod
    def validate_container_id(cls, v):
        """Validate container ID format"""
        if not v or len(v) < 12:
            raise ValueError("Invalid container ID format")
        return v


class ValidationResponse(BaseModel):
    """Complete validation response"""

    validation_id: str
    task_id: int
    user_id: int
    status: ValidationStatus
    total_score: float = Field(..., ge=0, le=100)
    checks: List[ValidationCheck]
    feedback: str
    details: Dict[str, Any]
    started_at: datetime
    completed_at: datetime
    duration_ms: int


class ValidationResult(BaseModel):
    """Internal validation result"""

    status: ValidationStatus
    score: float
    checks: List[ValidationCheck]
    feedback: str
    details: Dict[str, Any]


class TaskInfo(BaseModel):
    """Task information from Task Service"""

    id: int
    title: str
    description: str
    task_type: str
    docker_image: str
    points: int
    difficulty: str
    validation_config: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(BaseModel):
    """Error response for validation failures"""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
