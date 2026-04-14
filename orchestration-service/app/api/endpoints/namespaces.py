"""Namespace management endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging

from app.models.schemas import NamespaceRequest, NamespaceResponse, NamespaceStatus
from app.api.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=NamespaceResponse)
async def create_namespace(
    request: NamespaceRequest, current_user: dict = Depends(get_current_user)
):
    """Create a namespace for a user"""
    # Simplified implementation
    namespace_name = f"student-{request.user_id}"

    return NamespaceResponse(
        namespace=namespace_name,
        user_id=request.user_id,
        username=request.username,
        status=NamespaceStatus.ACTIVE,
        created_at=datetime.utcnow(),
        containers_count=0,
        resource_usage={},
    )


@router.get("/{user_id}", response_model=NamespaceResponse)
async def get_namespace(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get namespace for a user"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    namespace_name = f"student-{user_id}"

    return NamespaceResponse(
        namespace=namespace_name,
        user_id=user_id,
        username=current_user.get("username", "user"),
        status=NamespaceStatus.ACTIVE,
        created_at=datetime.utcnow(),
        containers_count=0,
        resource_usage={},
    )


@router.delete("/{user_id}")
async def delete_namespace(
    user_id: int, current_user: dict = Depends(get_current_user)
):
    """Delete a namespace"""
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return {"message": f"Namespace student-{user_id} deleted"}


from datetime import datetime
