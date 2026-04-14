import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.main import app
from src.core.database import Base, get_db
from src.core.security import get_current_user, get_current_admin_user

# Тестовая БД - используем файл вместо :memory:
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создаем движок
engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Создаем таблицы перед каждым тестом"""
    # Используем sync_begin для SQLite
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Очищаем после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Сессия с autocommit=False для контроля транзакций"""
    async with TestingSessionLocal() as session:
        # Не начинаем транзакцию явно, SQLite сделает это автоматически
        yield session
        await session.commit()  # Коммитим изменения
        await session.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "testuser",
        "role": "student",
        "is_active": True,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def admin_client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2,
        "username": "admin",
        "role": "admin",
        "is_active": True,
    }
    app.dependency_overrides[get_current_admin_user] = lambda: {
        "id": 2,
        "username": "admin",
        "role": "admin",
        "is_active": True,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_category(db_session: AsyncSession):
    from src.models.category import Category

    category = Category(name="Test Category", description="Test", icon="🔧")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_course(db_session: AsyncSession, test_category):
    """Фикстура для создания тестового курса"""
    from src.models.course import Course

    course = Course(
        title="Test Course",
        description="Test Course Description",
        difficulty="beginner",
        category_id=test_category.id,
        order=1,
        is_published=True,
        estimated_time_minutes=60,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course


@pytest.fixture
async def test_task(db_session: AsyncSession, test_course):
    """Фикстура для создания тестового задания"""
    from src.models.task import Task

    task = Task(
        title="Test Task",
        description="Test Task Description",
        task_type="hardening",
        course_id=test_course.id,
        order_in_course=1,
        docker_image="ubuntu:22.04",
        points=50,
        difficulty="easy",
        estimated_time_minutes=15,
        is_published=True,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task
