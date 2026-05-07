"""Container management service"""

import uuid
import asyncio
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from app.models.schemas import (
    ContainerRequest,
    ContainerResponse,
    ContainerStatus,
    ContainerMetrics,
)

logger = logging.getLogger(__name__)


class ContainerManager:
    """Manage container lifecycle -直接用 Docker CLI"""

    _containers: Dict[str, ContainerResponse] = {}
    _cleanup_task = None

    def __init__(self):
        self.containers = self.__class__._containers
        logger.info("ContainerManager initialized")

    async def start(self):
        if self.__class__._cleanup_task is None:
            self.__class__._cleanup_task = asyncio.create_task(
                self._cleanup_expired_containers()
            )
            logger.info("Container cleanup task started")

    async def stop(self):
        if self.__class__._cleanup_task:
            self.__class__._cleanup_task.cancel()
            try:
                await self.__class__._cleanup_task
            except asyncio.CancelledError:
                pass
            self.__class__._cleanup_task = None
            logger.info("Container cleanup task stopped")

    async def _run_cmd(self, cmd: list) -> tuple:
        """Запуск команды"""
        try:
            result = await asyncio.to_thread(
                subprocess.run, cmd, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    async def create_container(self, request: ContainerRequest) -> ContainerResponse:
        container_id = str(uuid.uuid4())[:12]
        container_name = f"task-{request.task_id}-{container_id}"
        expires_at = datetime.utcnow() + timedelta(seconds=request.timeout_seconds)

        # Реальное создание контейнера через Docker CLI
        success, stdout, stderr = await self._run_cmd(
            [
                "docker",
                "run",
                "-d",
                "--name",
                container_name,
                request.docker_image,
                "sleep",
                "infinity",
            ]
        )

        real_container_id = None
        if success:
            real_container_id = stdout.strip()
            logger.info(f"✅ Container created: {real_container_id[:12]}")
        else:
            logger.error(f"❌ Failed: {stderr}")

        connection_details = {
            "container_id": container_id,
            "name": container_name,
            "access_command": f"docker exec -it {container_name} /bin/bash",
            "docker_id": real_container_id,
        }

        response = ContainerResponse(
            container_id=container_id,
            task_id=request.task_id,
            user_id=request.user_id,
            name=container_name,
            namespace=f"student-{request.user_id}",
            status=ContainerStatus.RUNNING if success else ContainerStatus.ERROR,
            image=request.docker_image,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            connection_details=connection_details,
        )

        self.containers[container_id] = response
        return response

    async def get_container(
        self, container_id: str, user_id: int
    ) -> Optional[ContainerResponse]:
        container = self.containers.get(container_id)
        if not container or container.user_id != user_id:
            return None
        container.last_accessed = datetime.utcnow()
        return container

    async def list_user_containers(self, user_id: int) -> List[ContainerResponse]:
        return [
            c
            for c in self.containers.values()
            if c.user_id == user_id and c.status != ContainerStatus.DELETED
        ]

    async def delete_container(self, container_id: str, user_id: int):
        container = await self.get_container(container_id, user_id)
        if not container:
            return

        real_id = container.connection_details.get("docker_id")
        if real_id:
            await self._run_cmd(["docker", "stop", real_id])
            await self._run_cmd(["docker", "rm", real_id])
            logger.info(f"✅ Container removed: {real_id[:12]}")

        container.status = ContainerStatus.DELETED

        async def remove():
            await asyncio.sleep(5)
            if container_id in self.containers:
                del self.containers[container_id]

        asyncio.create_task(remove())

    async def _cleanup_expired_containers(self):
        while True:
            try:
                now = datetime.utcnow()
                for cid, c in list(self.containers.items()):
                    if now > c.expires_at and c.status != ContainerStatus.DELETED:
                        await self.delete_container(cid, c.user_id)
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(60)

    async def get_container_metrics(
        self, container_id: str, user_id: int
    ) -> Optional[ContainerMetrics]:
        container = await self.get_container(container_id, user_id)
        if not container:
            return None
        return ContainerMetrics(
            container_id=container_id,
            cpu_usage=0.5,
            memory_usage=128 * 1024 * 1024,
            memory_limit=512 * 1024 * 1024,
            network_rx=1024,
            network_tx=512,
            uptime_seconds=3600,
            timestamp=datetime.utcnow(),
        )
