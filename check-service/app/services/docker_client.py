"""Docker client for container operations"""

import docker
from typing import Dict, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class DockerClient:
    """Docker client wrapper"""

    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None

    async def exec_command(
        self, container_id: str, command: str, timeout: int = 30
    ) -> Dict[str, Any]:
        """Execute command in container"""
        try:
            loop = asyncio.get_event_loop()

            def sync_exec():
                container = self.client.containers.get(container_id)
                exec_result = container.exec_run(command, stdout=True, stderr=True)
                return {
                    "stdout": exec_result.output.decode("utf-8", errors="ignore"),
                    "stderr": "",
                    "exit_code": exec_result.exit_code,
                }

            result = await loop.run_in_executor(None, sync_exec)
            return result

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {"stdout": "", "stderr": str(e), "exit_code": -1}

    async def container_exists(self, container_id: str) -> bool:
        """Check if container exists"""
        try:
            self.client.containers.get(container_id)
            return True
        except:
            return False
