import logging
from datetime import datetime
import uuid
import subprocess
import re

from app.models.schemas import (
    ValidationRequest,
    ValidationResponse,
    ValidationStatus,
    ValidationCheck,
)

logger = logging.getLogger(__name__)


class ValidationService:
    async def validate(self, request: ValidationRequest) -> ValidationResponse:
        start_time = datetime.utcnow()
        validation_id = str(uuid.uuid4())

        try:
            # Ищем контейнер по имени или короткому ID
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.ID}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            container_name = None
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("\t")
                name = parts[0] if len(parts) > 0 else ""
                full_id = parts[1] if len(parts) > 1 else ""

                if request.container_id in name or request.container_id in full_id:
                    container_name = name
                    break

            if not container_name:
                return self._error_response(
                    validation_id,
                    request,
                    start_time,
                    f"Container {request.container_id} not found",
                )

            logger.info(f"Found container: {container_name}")

        except Exception as e:
            return self._error_response(
                validation_id, request, start_time, f"Docker error: {e}"
            )

        checks = []
        score = 0

        # Проверка 1: PermitRootLogin no
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "grep",
                "-c",
                "^PermitRootLogin no",
                "/etc/ssh/sshd_config",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if (
            result.returncode == 0
            and result.stdout.strip()
            and int(result.stdout.strip()) > 0
        ):
            score += 20
            checks.append(
                ValidationCheck(
                    check_id="root_login",
                    name="PermitRootLogin",
                    status=ValidationStatus.PASSED,
                    message="PermitRootLogin is set to no",
                    points=20,
                    max_points=20,
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="root_login",
                    name="PermitRootLogin",
                    status=ValidationStatus.FAILED,
                    message="PermitRootLogin should be set to no",
                    points=0,
                    max_points=20,
                )
            )

        # Проверка 2: PasswordAuthentication no
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "grep",
                "-c",
                "^PasswordAuthentication no",
                "/etc/ssh/sshd_config",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if (
            result.returncode == 0
            and result.stdout.strip()
            and int(result.stdout.strip()) > 0
        ):
            score += 20
            checks.append(
                ValidationCheck(
                    check_id="password_auth",
                    name="PasswordAuthentication",
                    status=ValidationStatus.PASSED,
                    message="PasswordAuthentication is set to no",
                    points=20,
                    max_points=20,
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="password_auth",
                    name="PasswordAuthentication",
                    status=ValidationStatus.FAILED,
                    message="PasswordAuthentication should be set to no",
                    points=0,
                    max_points=20,
                )
            )

        # Проверка 3: Port 2222
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "grep",
                "-c",
                "^Port 2222",
                "/etc/ssh/sshd_config",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if (
            result.returncode == 0
            and result.stdout.strip()
            and int(result.stdout.strip()) > 0
        ):
            score += 20
            checks.append(
                ValidationCheck(
                    check_id="port",
                    name="SSH Port",
                    status=ValidationStatus.PASSED,
                    message="SSH port is set to 2222",
                    points=20,
                    max_points=20,
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="port",
                    name="SSH Port",
                    status=ValidationStatus.FAILED,
                    message="SSH port should be 2222",
                    points=0,
                    max_points=20,
                )
            )

        # Проверка 4: AllowUsers exists
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "grep",
                "-c",
                "^AllowUsers",
                "/etc/ssh/sshd_config",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if (
            result.returncode == 0
            and result.stdout.strip()
            and int(result.stdout.strip()) > 0
        ):
            score += 20
            checks.append(
                ValidationCheck(
                    check_id="allow_users",
                    name="AllowUsers",
                    status=ValidationStatus.PASSED,
                    message="AllowUsers is configured",
                    points=20,
                    max_points=20,
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="allow_users",
                    name="AllowUsers",
                    status=ValidationStatus.FAILED,
                    message="AllowUsers should be configured",
                    points=0,
                    max_points=20,
                )
            )

        # Проверка 5: MaxAuthTries <= 3
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "grep",
                "-E",
                "^MaxAuthTries ([0-9]+)",
                "/etc/ssh/sshd_config",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            match = re.search(r"MaxAuthTries (\d+)", result.stdout)
            if match and int(match.group(1)) <= 3:
                score += 20
                checks.append(
                    ValidationCheck(
                        check_id="max_auth_tries",
                        name="MaxAuthTries",
                        status=ValidationStatus.PASSED,
                        message=f"MaxAuthTries is {match.group(1)} (≤3)",
                        points=20,
                        max_points=20,
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        check_id="max_auth_tries",
                        name="MaxAuthTries",
                        status=ValidationStatus.FAILED,
                        message="MaxAuthTries should be ≤3",
                        points=0,
                        max_points=20,
                    )
                )
        else:
            checks.append(
                ValidationCheck(
                    check_id="max_auth_tries",
                    name="MaxAuthTries",
                    status=ValidationStatus.FAILED,
                    message="MaxAuthTries not configured",
                    points=0,
                    max_points=20,
                )
            )

        total_score = score
        status = (
            ValidationStatus.PASSED if total_score >= 80 else ValidationStatus.FAILED
        )

        feedback_lines = [f"SSH Hardening: {score}/100 points\n"]
        for check in checks:
            icon = "✅" if check.status == ValidationStatus.PASSED else "❌"
            feedback_lines.append(f"{icon} {check.message}")

        if total_score >= 80:
            feedback_lines.append("\n🎉 SSH is secure!")
        else:
            feedback_lines.append("\n⚠️ Please fix the failing checks.")

        return ValidationResponse(
            validation_id=validation_id,
            task_id=request.task_id,
            user_id=request.user_id,
            status=status,
            total_score=total_score,
            checks=checks,
            feedback="\n".join(feedback_lines),
            details={"container_name": container_name},
            started_at=start_time,
            completed_at=datetime.utcnow(),
            duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
        )

    def _error_response(self, validation_id, request, start_time, error_msg):
        return ValidationResponse(
            validation_id=validation_id,
            task_id=request.task_id,
            user_id=request.user_id,
            status=ValidationStatus.ERROR,
            total_score=0.0,
            checks=[],
            feedback=f"Error: {error_msg}",
            details={},
            started_at=start_time,
            completed_at=datetime.utcnow(),
            duration_ms=0,
        )
