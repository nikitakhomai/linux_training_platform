"""Container management endpoints"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from typing import List
import logging
import asyncio
import subprocess

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


@router.websocket("/ws/{container_id}")
async def websocket_terminal(websocket: WebSocket, container_id: str):
    """WebSocket endpoint for terminal access"""
    await websocket.accept()

    try:
        manager = ContainerManager()
        await manager.start()

        container_info = manager.containers.get(container_id)
        if not container_info:
            await websocket.send_text("Container not found")
            await websocket.close()
            return

        container_name = container_info.name

        await websocket.send_text(
            f"\x1b[32m✅ Connected to: {container_name}\x1b[0m\r\n"
        )
        await websocket.send_text(f"\x1b[33mInteractive shell ready!\x1b[0m\r\n")
        await websocket.send_text(f"\x1b[36m$ \x1b[0m")

        def execute_command(cmd: str) -> str:
            """Выполняет команду в контейнере"""
            try:
                result = subprocess.run(
                    ["docker", "exec", container_name, "sh", "-c", cmd],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                output = result.stdout
                if result.stderr:
                    output += result.stderr
                return output
            except subprocess.TimeoutExpired:
                return "Command timed out\n"
            except Exception as e:
                return f"Error: {str(e)}\n"

        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_text("pong")
            elif data.startswith("cmd:"):
                cmd = data[4:].strip()
                if cmd:
                    output = execute_command(cmd)
                    await websocket.send_text(output)
                await websocket.send_text("\x1b[36m$ \x1b[0m")
            else:
                # Если команда без префикса, тоже выполняем
                if data.strip():
                    output = execute_command(data.strip())
                    await websocket.send_text(output)
                await websocket.send_text("\x1b[36m$ \x1b[0m")

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# Остальные эндпоинты
@router.post("/", response_model=ContainerResponse, status_code=status.HTTP_201_CREATED)
async def create_container(
    request: ContainerRequest,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    logger.info(
        f"Creating container for user {current_user['id']}, task {request.task_id}"
    )
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
    try:
        container = await manager.get_container(container_id, current_user["id"])
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        return container
    except ContainerError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{container_id}", response_model=dict)
async def delete_container(
    container_id: str,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    try:
        await manager.delete_container(container_id, current_user["id"])
        return {
            "message": "Container deleted successfully",
            "container_id": container_id,
        }
    except ContainerError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{container_id}/action", response_model=ContainerResponse)
async def action_on_container(
    container_id: str,
    action: ContainerAction,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    try:
        container = await manager.get_container(container_id, current_user["id"])
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
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
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{container_id}/metrics", response_model=ContainerMetrics)
async def get_container_metrics(
    container_id: str,
    manager: ContainerManager = Depends(get_container_manager),
    current_user: dict = Depends(get_current_user),
):
    try:
        metrics = await manager.get_container_metrics(container_id, current_user["id"])
        if not metrics:
            raise HTTPException(status_code=404, detail="Metrics not available")
        return metrics
    except ContainerError as e:
        raise HTTPException(status_code=404, detail=str(e))
