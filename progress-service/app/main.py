"""Progress Service - Track student progress and achievements"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.endpoints import progress, leaderboard, analytics
from app.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL), format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Progress Service",
    description="""
    Service for tracking student progress in Linux security training.
    
    Features:
    * Track completed tasks and courses
    * Calculate skill matrix
    * Leaderboards and achievements
    * Personalized recommendations
    * Analytics for teachers
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(
    leaderboard.router, prefix="/api/v1/leaderboard", tags=["leaderboard"]
)
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "progress": "/api/v1/progress",
            "leaderboard": "/api/v1/leaderboard",
            "analytics": "/api/v1/analytics",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
