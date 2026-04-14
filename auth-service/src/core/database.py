from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.core.config import settings
from src.core.base import Base  # Импортируем Base из отдельного файла

# Создаем асинхронный движок
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency для получения сессии БД
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
