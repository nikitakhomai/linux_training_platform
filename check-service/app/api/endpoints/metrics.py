from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def metrics():
    return {"service": "check-service", "metrics": {}}
