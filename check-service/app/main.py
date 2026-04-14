"""Check Service - Linux Security Validation Service"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Linux Security Check Service",
    description="Service for validating Linux security tasks",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Linux Security Check Service",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/v1/validation/types")
async def get_validation_types():
    """Get available validation types"""
    return {
        "validation_types": [
            {
                "id": "ssh_config",
                "name": "SSH Configuration",
                "description": "Validate SSH security settings",
            },
            {
                "id": "file_permissions",
                "name": "File Permissions",
                "description": "Check file and directory permissions",
            },
            {
                "id": "firewall_rules",
                "name": "Firewall Rules",
                "description": "Validate firewall configuration",
            },
        ]
    }


@app.post("/api/v1/validation/validate")
async def validate_task(request: dict):
    """Validate a task solution"""
    return {
        "validation_id": "test-123",
        "task_id": request.get("task_id", 1),
        "user_id": request.get("user_id", 1),
        "status": "passed",
        "total_score": 85.5,
        "checks": [
            {
                "check_id": "ssh_protocol",
                "name": "SSH Protocol",
                "status": "passed",
                "message": "Protocol 2 is configured",
                "points": 10,
                "max_points": 10,
            }
        ],
        "feedback": "Great job! Most checks passed.",
        "details": {},
        "started_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:00:01Z",
        "duration_ms": 1000,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
