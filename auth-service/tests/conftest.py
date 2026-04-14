import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.main import app
from src.core.base import Base
from src.core.database import get_db
from src.core.security import (
    get_current_user,
    get_current_admin_user,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from src.models.user import User, UserRole

# Тестовая БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    print("\n" + "=" * 50)
    print("СОЗДАНИЕ ТАБЛИЦ")
    print("=" * 50)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("=" * 50 + "\n")
    yield
    print("\n" + "=" * 50)
    print("ОЧИСТКА")
    print("=" * 50)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("=" * 50 + "\n")


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session


# ВАЖНО: Убираем фикстуры test_user и test_admin, чтобы не создавали конфликтов!
# Вместо них создаем пользователей прямо в тестах, где нужно


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()


# Фикстура для создания тестового пользователя (для тестов, где нужен существующий пользователь)
@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        username="existinguser",
        email="existing@example.com",
        full_name="Existing User",
        hashed_password=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# Фикстура для создания тестового администратора
@pytest.fixture
async def test_admin(db_session: AsyncSession) -> User:
    admin = User(
        username="existingadmin",
        email="admin@example.com",
        full_name="Existing Admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


# Клиент без авторизации
@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# Клиент с токеном обычного пользователя
@pytest.fixture
async def auth_client(test_user) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db

    token_data = {"sub": test_user.username, "role": test_user.role.value}
    access_token = create_access_token(token_data)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# Клиент с токеном администратора
@pytest.fixture
async def admin_client(test_admin) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db

    token_data = {"sub": test_admin.username, "role": test_admin.role.value}
    access_token = create_access_token(token_data)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
