"""Orchestration Service - Container Management for Security Training"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.endpoints import containers, namespaces, health
from app.config import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL), format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Kubernetes mode: {settings.KUBERNETES_MODE}")

    yield

    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Orchestration Service",
    description="Service for managing isolated containers for Linux security training",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(containers.router, prefix="/api/v1/containers", tags=["containers"])
app.include_router(namespaces.router, prefix="/api/v1/namespaces", tags=["namespaces"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "mode": settings.KUBERNETES_MODE,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "containers": "/api/v1/containers",
            "namespaces": "/api/v1/namespaces",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
