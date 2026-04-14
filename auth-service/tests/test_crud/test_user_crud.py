import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.user import crud_user
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import verify_password

pytestmark = pytest.mark.asyncio


class TestUserCRUD:
    """Тесты CRUD операций для пользователей"""

    async def test_create_user(self, db_session: AsyncSession):
        """Создание пользователя"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            full_name="Test User",
            role="student",
        )

        user = await crud_user.create(db_session, user_in)

        assert user.id is not None
        assert user.username == user_in.username
        assert user.email == user_in.email
        assert user.full_name == user_in.full_name
        assert user.role.value == user_in.role
        assert user.is_active is True
        assert user.is_verified is False
        assert verify_password("password123", user.hashed_password) is True

    async def test_get_user_by_id(self, db_session: AsyncSession, test_user):
        """Получение пользователя по ID"""
        user = await crud_user.get_by_id(db_session, test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    async def test_get_user_by_username(self, db_session: AsyncSession, test_user):
        """Получение пользователя по username"""
        user = await crud_user.get_by_username(db_session, test_user.username)

        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    async def test_get_user_by_email(self, db_session: AsyncSession, test_user):
        """Получение пользователя по email"""
        user = await crud_user.get_by_email(db_session, test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_get_user_not_found(self, db_session: AsyncSession):
        """Получение несуществующего пользователя"""
        user = await crud_user.get_by_id(db_session, 99999)
        assert user is None

    async def test_update_user(self, db_session: AsyncSession, test_user):
        """Обновление пользователя"""
        update_data = UserUpdate(full_name="Updated Name", email="updated@example.com")

        updated = await crud_user.update(db_session, test_user.id, update_data)

        assert updated is not None
        assert updated.full_name == "Updated Name"
        assert updated.email == "updated@example.com"
        assert updated.username == test_user.username  # Не изменилось

    async def test_update_user_password(self, db_session: AsyncSession, test_user):
        """Обновление пароля пользователя"""
        update_data = UserUpdate(password="newpassword123")

        updated = await crud_user.update(db_session, test_user.id, update_data)

        assert updated is not None
        assert verify_password("newpassword123", updated.hashed_password) is True

    async def test_authenticate_user_success(self, db_session: AsyncSession, test_user):
        """Успешная аутентификация"""
        user = await crud_user.authenticate(
            db_session, username=test_user.username, password="password123"
        )

        assert user is not None
        assert user.id == test_user.id

    async def test_authenticate_user_wrong_password(
        self, db_session: AsyncSession, test_user
    ):
        """Аутентификация с неверным паролем"""
        user = await crud_user.authenticate(
            db_session, username=test_user.username, password="wrongpassword"
        )

        assert user is None

    async def test_authenticate_user_not_found(self, db_session: AsyncSession):
        """Аутентификация несуществующего пользователя"""
        user = await crud_user.authenticate(
            db_session, username="nonexistent", password="password123"
        )

        assert user is None
