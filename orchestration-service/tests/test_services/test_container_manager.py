"""Tests for Container Manager"""

import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import pytest
import asyncio
from app.services.container_manager import ContainerManager
from app.models.schemas import ContainerRequest


@pytest.fixture
async def manager():
    """Create and cleanup container manager"""
    mgr = ContainerManager()
    await mgr.start()
    yield mgr
    await mgr.stop()


@pytest.mark.asyncio
async def test_create_container(manager):
    """Test container creation"""
    request = ContainerRequest(
        task_id=1, user_id=1, docker_image="ubuntu:22.04", timeout_seconds=3600
    )

    container = await manager.create_container(request)

    assert container is not None
    assert container.container_id is not None
    assert container.task_id == 1
    assert container.user_id == 1
    assert container.status == "running"

    # Cleanup
    await manager.delete_container(container.container_id, 1)


@pytest.mark.asyncio
async def test_list_user_containers(manager):
    """Test listing containers"""
    # Create a container
    request = ContainerRequest(task_id=1, user_id=1)
    container1 = await manager.create_container(request)

    # List containers
    containers = await manager.list_user_containers(1)
    assert len(containers) >= 1

    # Create another container
    request2 = ContainerRequest(task_id=2, user_id=1)
    container2 = await manager.create_container(request2)

    # List again
    containers = await manager.list_user_containers(1)
    assert len(containers) >= 2

    # Cleanup
    await manager.delete_container(container1.container_id, 1)
    await manager.delete_container(container2.container_id, 1)


@pytest.mark.asyncio
async def test_get_container(manager):
    """Test getting container"""
    # Create container
    request = ContainerRequest(task_id=1, user_id=1)
    container = await manager.create_container(request)

    # Get it
    retrieved = await manager.get_container(container.container_id, 1)
    assert retrieved is not None
    assert retrieved.container_id == container.container_id

    # Cleanup
    await manager.delete_container(container.container_id, 1)


@pytest.mark.asyncio
async def test_get_container_wrong_user(manager):
    """Test access denied for wrong user"""
    # Create container
    request = ContainerRequest(task_id=1, user_id=1)
    container = await manager.create_container(request)

    # Try to get with wrong user
    retrieved = await manager.get_container(container.container_id, 999)
    assert retrieved is None

    # Cleanup
    await manager.delete_container(container.container_id, 1)


@pytest.mark.asyncio
async def test_delete_container(manager):
    """Test deleting container"""
    # Create container
    request = ContainerRequest(task_id=1, user_id=1)
    container = await manager.create_container(request)

    # Delete it
    await manager.delete_container(container.container_id, 1)

    # Try to get it (should return None)
    retrieved = await manager.get_container(container.container_id, 1)
    assert retrieved is None


@pytest.mark.asyncio
async def test_container_expiration(manager):
    """Test container expiration"""
    # Create container with short timeout
    request = ContainerRequest(task_id=1, user_id=1, timeout_seconds=1)
    container = await manager.create_container(request)

    # Wait for expiration
    await asyncio.sleep(2)

    # Try to get it (should return None)
    retrieved = await manager.get_container(container.container_id, 1)
    assert retrieved is None
