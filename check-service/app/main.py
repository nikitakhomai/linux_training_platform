"""Check Service - Linux Security Validation Service"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.endpoints import validation, health
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Check Service...")
    yield
    logger.info("Shutting down Check Service...")


app = FastAPI(
    title="Linux Security Check Service",
    description="Service for validating Linux security tasks",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(validation.router, prefix="/api/v1/validation", tags=["validation"])
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    return {
        "service": "Linux Security Check Service",
        "version": "1.0.0",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
