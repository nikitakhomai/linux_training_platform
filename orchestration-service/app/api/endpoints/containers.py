"""Container management endpoints - Simplified"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.models.schemas import (
    ContainerRequest,
    ContainerResponse,
    ContainerListResponse,
    ContainerAction,
    ContainerMetrics,
)
from app.services.container_manager import ContainerManager
from app.api.dependencies import get_container_manager, get_current_user
from app.core.exceptions import ContainerError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ContainerResponse, status_code=status.HTTP_201_CREATED)
async def create_container(
    request: ContainerRequest,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    """Create a new container for a task"""
    logger.info(
        f"Creating container for user {current_user['id']}, task {request.task_id}"
    )

    # Override user_id from token for security
    request.user_id = current_user["id"]

    try:
        container = await manager.create_container(request)
        return container
    except ContainerError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error"
        )


@router.get("/", response_model=ContainerListResponse)
async def list_containers(
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    """List all containers for current user"""
    containers = await manager.list_user_containers(current_user["id"])

    active = len([c for c in containers if c.status not in ["deleted", "error"]])

    return ContainerListResponse(
        containers=containers, total=len(containers), active=active
    )


@router.get("/{container_id}", response_model=ContainerResponse)
async def get_container(
    container_id: str,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get container details"""
    try:
        container = await manager.get_container(container_id, current_user["id"])
        if not container:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Container not found"
            )
        return container
    except ContainerError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{container_id}", response_model=dict)
async def delete_container(
    container_id: str,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    """Delete a container"""
    try:
        await manager.delete_container(container_id, current_user["id"])
        return {
            "message": "Container deleted successfully",
            "container_id": container_id,
        }
    except ContainerError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{container_id}/action", response_model=ContainerResponse)
async def action_on_container(
    container_id: str,
    action: ContainerAction,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    """Perform action on container (start/stop/restart/delete)"""
    try:
        container = await manager.get_container(container_id, current_user["id"])

        if not container:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Container not found"
            )

        if action.action == "delete":
            await manager.delete_container(container_id, current_user["id"])
            container.status = "deleted"
        elif action.action == "stop":
            container.status = "stopped"
        elif action.action == "start":
            container.status = "running"
        elif action.action == "restart":
            container.status = "running"

        return container

    except ContainerError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{container_id}/metrics", response_model=ContainerMetrics)
async def get_container_metrics(
    container_id: str,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get container metrics"""
    try:
        metrics = await manager.get_container_metrics(container_id, current_user["id"])
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Metrics not available"
            )
        return metrics
    except ContainerError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
