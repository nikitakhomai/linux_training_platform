"""Tests for Container Manager"""

import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from app.services.container_manager import ContainerManager
from app.models.schemas import ContainerRequest


# Simple mock container class
class MockContainerInfo:
    def __init__(self, container_id, task_id, user_id, status):
        self.container_id = container_id
        self.task_id = task_id
        self.user_id = user_id
        self.status = status
        self.created_at = None


@pytest.fixture
async def manager():
    """Create and cleanup container manager with mocked Docker"""
    with patch("app.services.container_manager.aiodocker.Docker") as MockDocker:
        # Create mock Docker client
        mock_docker = AsyncMock()
        mock_docker.containers = AsyncMock()
        mock_docker.containers.create = AsyncMock()
        mock_docker.containers.get = AsyncMock()

        # Setup mock container
        mock_container = AsyncMock()
        mock_container.id = "test_container_123"
        mock_container.status = "running"
        mock_docker.containers.create.return_value = mock_container
        mock_docker.containers.get.return_value = mock_container

        MockDocker.return_value = mock_docker

        mgr = ContainerManager()
        # Initialize containers dict
        mgr.containers = {}
        await mgr.start()

        # Return the manager directly, not an async generator
        return mgr


@pytest.fixture
async def cleanup_manager():
    """Fixture that yields and then cleans up"""
    mgr = await manager()
    yield mgr
    await mgr.stop()


# @pytest.mark.asyncio
# async def test_create_container():
#     """Test container creation - using direct manager creation"""
#     with patch("app.services.container_manager.aiodocker.Docker") as MockDocker:
#         # Create mock Docker client
#         mock_docker = AsyncMock()
#         mock_docker.containers = AsyncMock()
#         mock_docker.containers.create = AsyncMock()
#         mock_container = AsyncMock()
#         mock_container.id = "test_container_123"
#         mock_docker.containers.create.return_value = mock_container
#         MockDocker.return_value = mock_docker
#
#         mgr = ContainerManager()
#         mgr.containers = {}
#         await mgr.start()
#
#         request = ContainerRequest(
#             task_id=1, user_id=1, docker_image="ubuntu:22.04", timeout_seconds=3600
#         )
#
#         # Mock the _create_docker_container method
#         with patch.object(
#             mgr, "_create_docker_container", new_callable=AsyncMock
#         ) as mock_create:
#             mock_create.return_value = "test_container_123"
#             container = await mgr.create_container(request)
#
#         assert container is not None
#         assert container.container_id is not None
#         assert container.task_id == 1
#         assert container.user_id == 1
#         assert container.status in ["running", "starting", "created"]
#
#         await mgr.stop()


@pytest.mark.asyncio
async def test_list_user_containers():
    """Test listing containers"""
    mgr = ContainerManager()
    mgr.containers = {}

    # Create mock containers
    container1 = MockContainerInfo(
        container_id="test1", task_id=1, user_id=1, status="running"
    )
    container2 = MockContainerInfo(
        container_id="test2", task_id=2, user_id=1, status="running"
    )

    mgr.containers["test1"] = container1
    mgr.containers["test2"] = container2

    # List containers
    containers = await mgr.list_user_containers(1)
    assert len(containers) >= 2
    assert all(c.user_id == 1 for c in containers)


@pytest.mark.asyncio
async def test_get_container():
    """Test getting container"""
    mgr = ContainerManager()
    mgr.containers = {}

    # Create mock container
    container = MockContainerInfo(
        container_id="test_container", task_id=1, user_id=1, status="running"
    )
    mgr.containers["test_container"] = container

    # Get it
    retrieved = await mgr.get_container("test_container", 1)
    assert retrieved is not None
    assert retrieved.container_id == container.container_id


@pytest.mark.asyncio
async def test_get_container_wrong_user():
    """Test access denied for wrong user"""
    mgr = ContainerManager()
    mgr.containers = {}

    # Create mock container
    container = MockContainerInfo(
        container_id="test_container", task_id=1, user_id=1, status="running"
    )
    mgr.containers["test_container"] = container

    # Try to get with wrong user
    retrieved = await mgr.get_container("test_container", 999)
    assert retrieved is None


# @pytest.mark.asyncio
# async def test_delete_container():
#     """Test deleting container"""
#     mgr = ContainerManager()
#     mgr.containers = {}
#
#     # Create mock container
#     container = MockContainerInfo(
#         container_id="test_container", task_id=1, user_id=1, status="running"
#     )
#     mgr.containers["test_container"] = container
#
#     # Mock the stop method if it exists
#     if hasattr(mgr, "_stop_docker_container"):
#         with patch.object(mgr, "_stop_docker_container", new_callable=AsyncMock):
#             await mgr.delete_container("test_container", 1)
#     else:
#         await mgr.delete_container("test_container", 1)
#
#     # Try to get it (should return None)
#     retrieved = await mgr.get_container("test_container", 1)
#     assert retrieved is None
#
#
# @pytest.mark.asyncio
# async def test_container_expiration():
#     """Test container expiration"""
#     mgr = ContainerManager()
#     mgr.containers = {}
#
#     # Create container
#     container = MockContainerInfo(
#         container_id="test_container", task_id=1, user_id=1, status="running"
#     )
#     container.created_at = asyncio.get_event_loop().time() - 10  # 10 seconds ago
#     mgr.containers["test_container"] = container
#
#     # Run cleanup
#     if hasattr(mgr, "_cleanup_expired_containers"):
#         await mgr._cleanup_expired_containers()
#     elif hasattr(mgr, "cleanup_expired"):
#         await mgr.cleanup_expired()
#
#     # Container should be removed
#     retrieved = await mgr.get_container("test_container", 1)
#     assert retrieved is None
