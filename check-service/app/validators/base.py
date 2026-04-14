"""Base validator class for all validators"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

from app.models.schemas import ValidationCheck, ValidationStatus, ValidationResult


logger = logging.getLogger(__name__)


@dataclass
class ValidationContext:
    """Context for validation execution"""

    container_id: str
    task_id: int
    user_id: int
    validation_config: Dict[str, Any] = field(default_factory=dict)
    task_info: Optional[Dict[str, Any]] = None


class BaseValidator(ABC):
    """Base abstract validator class"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.checks: List[Dict[str, Any]] = []

    @abstractmethod
    async def validate(self, context: ValidationContext) -> ValidationResult:
        """
        Execute validation logic
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def _execute_check(
        self, command: str, context: ValidationContext
    ) -> Dict[str, Any]:
        """
        Execute a single check in container
        """
        pass

    def create_check(
        self,
        check_id: str,
        name: str,
        status: ValidationStatus,
        message: str,
        points: int = 0,
        max_points: int = 10,
        details: Optional[Dict[str, Any]] = None,
    ) -> ValidationCheck:
        """Create a validation check result"""
        return ValidationCheck(
            check_id=check_id,
            name=name,
            status=status,
            message=message,
            points=points,
            max_points=max_points,
            details=details,
        )

    def calculate_score(self, checks: List[ValidationCheck]) -> float:
        """Calculate total score from checks"""
        if not checks:
            return 0.0

        total_points = sum(check.points for check in checks)
        total_max_points = sum(check.max_points for check in checks)

        if total_max_points == 0:
            return 0.0

        return (total_points / total_max_points) * 100

    def generate_feedback(self, checks: List[ValidationCheck]) -> str:
        """Generate detailed feedback message"""
        passed = sum(1 for c in checks if c.status == ValidationStatus.PASSED)
        failed = sum(1 for c in checks if c.status == ValidationStatus.FAILED)

        feedback_lines = [
            f"Validation Results: {passed}/{len(checks)} checks passed",
            f"Total Score: {self.calculate_score(checks):.1f}%",
            "",
            "Detailed Results:",
        ]

        for check in checks:
            status_icon = "✅" if check.status == ValidationStatus.PASSED else "❌"
            feedback_lines.append(f"{status_icon} {check.name}: {check.message}")

            if check.details:
                for key, value in check.details.items():
                    feedback_lines.append(f"   • {key}: {value}")

        return "\n".join(feedback_lines)
