"""Docker client for container operations"""

import docker
from typing import Dict, Any
import logging

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
        """Execute command in container and return result"""
        import asyncio

        if not self.client:
            return {
                "stdout": "",
                "stderr": "Docker client not available",
                "exit_code": -1,
            }

        try:
            loop = asyncio.get_event_loop()

            def sync_exec():
                try:
                    container = self.client.containers.get(container_id)
                    exec_result = container.exec_run(
                        command, stdout=True, stderr=True, demux=False
                    )
                    # Декодируем вывод
                    output = exec_result.output
                    if output:
                        try:
                            output = output.decode("utf-8", errors="ignore")
                        except:
                            output = str(output)
                    else:
                        output = ""

                    return {
                        "stdout": output,
                        "stderr": "",
                        "exit_code": exec_result.exit_code,
                    }
                except Exception as e:
                    logger.error(f"Command execution error: {e}")
                    return {"stdout": "", "stderr": str(e), "exit_code": -1}

            result = await loop.run_in_executor(None, sync_exec)
            logger.info(
                f"Executed in {container_id}: {command[:50]}... exit={result['exit_code']}"
            )
            return result

        except Exception as e:
            logger.error(f"Async execution error: {e}")
            return {"stdout": "", "stderr": str(e), "exit_code": -1}
