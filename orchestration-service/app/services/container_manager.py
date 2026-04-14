"""Container management service"""

import uuid
import asyncio
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
    """Manage container lifecycle"""

    # Используем классовый атрибут для хранения контейнеров
    _containers: Dict[str, ContainerResponse] = {}
    _cleanup_task = None

    def __init__(self):
        # Используем классовый словарь, а не инстансный
        self.containers = self.__class__._containers
        logger.info(
            f"ContainerManager initialized. Current containers: {len(self.containers)}"
        )

    async def start(self):
        """Start background cleanup task"""
        if self.__class__._cleanup_task is None:
            self.__class__._cleanup_task = asyncio.create_task(
                self._cleanup_expired_containers()
            )
            logger.info("Container cleanup task started")

    async def stop(self):
        """Stop background cleanup task"""
        if self.__class__._cleanup_task:
            self.__class__._cleanup_task.cancel()
            try:
                await self.__class__._cleanup_task
            except asyncio.CancelledError:
                pass
            self.__class__._cleanup_task = None
            logger.info("Container cleanup task stopped")

    async def create_container(self, request: ContainerRequest) -> ContainerResponse:
        """Create a new container for task"""
        try:
            # Generate container ID and name
            container_id = str(uuid.uuid4())[:12]
            namespace = f"student-{request.user_id}"
            container_name = f"task-{request.task_id}-{container_id}"

            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(seconds=request.timeout_seconds)

            # Create response with mock connection details
            connection_details = {
                "container_id": container_id,
                "name": container_name,
                "namespace": namespace,
                "access_command": f"docker exec -it {container_name} /bin/bash",
                "status": "running",
            }

            # Create response
            response = ContainerResponse(
                container_id=container_id,
                task_id=request.task_id,
                user_id=request.user_id,
                name=container_name,
                namespace=namespace,
                status=ContainerStatus.RUNNING,
                image=request.docker_image,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                connection_details=connection_details,
            )

            # Store container info в классовый словарь
            self.containers[container_id] = response

            logger.info(
                f"Created container {container_id} for user {request.user_id}, task {request.task_id}"
            )
            logger.info(f"Total containers now: {len(self.containers)}")
            return response

        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            raise

    async def get_container(
        self, container_id: str, user_id: int
    ) -> Optional[ContainerResponse]:
        """Get container by ID with user validation"""
        logger.info(
            f"Getting container {container_id} for user {user_id}. Available: {list(self.containers.keys())}"
        )

        container = self.containers.get(container_id)

        if not container:
            logger.warning(f"Container {container_id} not found")
            return None

        if container.user_id != user_id:
            logger.warning(
                f"User {user_id} tried to access container {container_id} owned by {container.user_id}"
            )
            return None

        # Update last accessed time
        container.last_accessed = datetime.utcnow()

        # Check if expired
        if datetime.utcnow() > container.expires_at:
            logger.info(f"Container {container_id} has expired")
            await self.delete_container(container_id, user_id)
            return None

        return container

    async def list_user_containers(self, user_id: int) -> List[ContainerResponse]:
        """List all containers for a user"""
        user_containers = [
            c
            for c in self.containers.values()
            if c.user_id == user_id and c.status != ContainerStatus.DELETED
        ]

        logger.info(f"User {user_id} has {len(user_containers)} containers")
        return user_containers

    async def delete_container(self, container_id: str, user_id: int):
        """Delete a container"""
        container = await self.get_container(container_id, user_id)

        if not container:
            logger.warning(
                f"Cannot delete container {container_id}: not found or access denied"
            )
            return

        # Update status
        container.status = ContainerStatus.DELETED

        # Remove from tracking after delay
        async def remove_after_delay():
            await asyncio.sleep(5)  # Уменьшил задержку для тестов
            if container_id in self.containers:
                del self.containers[container_id]
                logger.info(f"Removed container {container_id} from storage")

        asyncio.create_task(remove_after_delay())

        logger.info(f"Deleted container {container_id}")

    async def _cleanup_expired_containers(self):
        """Background task to cleanup expired containers"""
        while True:
            try:
                now = datetime.utcnow()

                for container_id, container in list(self.containers.items()):
                    if (
                        now > container.expires_at
                        and container.status != ContainerStatus.DELETED
                    ):
                        logger.info(f"Cleaning up expired container {container_id}")
                        try:
                            await self.delete_container(container_id, container.user_id)
                        except Exception as e:
                            logger.error(f"Cleanup failed for {container_id}: {e}")

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(60)

    async def get_container_metrics(
        self, container_id: str, user_id: int
    ) -> Optional[ContainerMetrics]:
        """Get container metrics"""
        container = await self.get_container(container_id, user_id)

        if not container:
            return None

        # Mock metrics for development
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
