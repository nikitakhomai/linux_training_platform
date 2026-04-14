"""Firewall rules validator"""

from typing import Dict, Any
import logging
from app.validators.base import BaseValidator, ValidationContext
from app.models.schemas import ValidationResult, ValidationStatus, ValidationCheck
from app.services.docker_client import DockerClient

logger = logging.getLogger(__name__)


class FirewallValidator(BaseValidator):
    """Validate firewall configuration"""

    def __init__(self, docker_client: DockerClient):
        super().__init__(
            name="Firewall Validator",
            description="Validates firewall rules and configuration",
        )
        self.docker_client = docker_client

    async def validate(self, context: ValidationContext) -> ValidationResult:
        """Execute firewall validation"""
        logger.info(
            f"Starting firewall validation for container {context.container_id}"
        )

        checks = []

        # Check iptables rules
        iptables_check = await self._check_iptables(context)
        checks.append(iptables_check)

        # Check if firewall is running
        firewall_check = await self._check_firewall_status(context)
        checks.append(firewall_check)

        # Calculate results
        total_score = self.calculate_score(checks)
        status = (
            ValidationStatus.PASSED if total_score >= 70 else ValidationStatus.FAILED
        )
        feedback = self.generate_feedback(checks)

        return ValidationResult(
            status=status,
            score=total_score,
            checks=checks,
            feedback=feedback,
            details={},
        )

    async def _check_iptables(self, context: ValidationContext) -> ValidationCheck:
        """Check iptables rules"""
        try:
            result = await self.docker_client.exec_command(
                context.container_id,
                "iptables -L 2>/dev/null || echo 'IPTABLES_NOT_AVAILABLE'",
            )

            output = result.get("stdout", "")

            if "IPTABLES_NOT_AVAILABLE" in output or not output:
                return self.create_check(
                    "iptables",
                    "IPTables Rules",
                    ValidationStatus.FAILED,
                    "IPTables not available or no rules configured",
                    0,
                    10,
                )

            # Check if there are any rules
            if "Chain INPUT" in output and "Chain FORWARD" in output:
                return self.create_check(
                    "iptables",
                    "IPTables Rules",
                    ValidationStatus.PASSED,
                    "IPTables is configured",
                    10,
                    10,
                )
            else:
                return self.create_check(
                    "iptables",
                    "IPTables Rules",
                    ValidationStatus.FAILED,
                    "IPTables is not properly configured",
                    0,
                    10,
                )

        except Exception as e:
            return self.create_check(
                "iptables",
                "IPTables Rules",
                ValidationStatus.ERROR,
                f"Error checking iptables: {str(e)}",
                0,
                10,
            )

    async def _check_firewall_status(
        self, context: ValidationContext
    ) -> ValidationCheck:
        """Check if firewall service is running"""
        try:
            # Try to check ufw status
            result = await self.docker_client.exec_command(
                context.container_id,
                "ufw status 2>/dev/null || echo 'UFW_NOT_AVAILABLE'",
            )

            output = result.get("stdout", "")

            if "UFW_NOT_AVAILABLE" in output:
                return self.create_check(
                    "firewall_service",
                    "Firewall Service",
                    ValidationStatus.PASSED,
                    "No firewall service detected (optional)",
                    10,
                    10,
                )
            elif "active" in output.lower():
                return self.create_check(
                    "firewall_service",
                    "Firewall Service",
                    ValidationStatus.PASSED,
                    "Firewall is active",
                    10,
                    10,
                )
            else:
                return self.create_check(
                    "firewall_service",
                    "Firewall Service",
                    ValidationStatus.FAILED,
                    "Firewall is not active",
                    0,
                    10,
                )

        except Exception as e:
            return self.create_check(
                "firewall_service",
                "Firewall Service",
                ValidationStatus.ERROR,
                f"Error checking firewall status: {str(e)}",
                0,
                10,
            )

    async def _execute_check(
        self, command: str, context: ValidationContext
    ) -> Dict[str, Any]:
        """Execute a check in container"""
        return await self.docker_client.exec_command(context.container_id, command)
