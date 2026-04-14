"""Health check endpoints"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "orchestration-service",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/readiness")
async def readiness_check():
    """Readiness probe"""
    return {"status": "ready"}


@router.get("/liveness")
async def liveness_check():
    """Liveness probe"""
    return {"status": "alive"}
