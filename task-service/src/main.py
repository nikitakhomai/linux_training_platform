from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.database import engine, Base
from src.api import tasks, courses, categories

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при старте
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Очистка при завершении
    await engine.dispose()

app = FastAPI(
    title="Task Service - Linux Security Training Platform",
    version="0.1.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])

@app.get("/")
async def root():
    return {
        "service": "task-service",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "task-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Другой порт, чем у auth-service
        reload=True
    )
