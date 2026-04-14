import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


class TestUsersAPI:
    """Тесты для API пользователей"""

    async def test_get_current_user(self, auth_client: AsyncClient, test_user):
        """Получение информации о текущем пользователе"""
        response = await auth_client.get("/users/me")

        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200
        data = response.json()

        # Сравниваем с данными из фикстуры test_user
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value

    async def test_get_current_user_unauthorized(
        self, client: AsyncClient
    ):  # ← ЭТОТ ТЕСТ УЖЕ ПРОХОДИТ
        """Получение информации без авторизации"""
        response = await client.get("/users/me")
        assert response.status_code == 401

    async def test_get_all_users_as_admin(
        self, admin_client: AsyncClient, test_user, test_admin
    ):
        """Админ получает список всех пользователей"""
        # Пользователи уже созданы фикстурами test_user и test_admin
        response = await admin_client.get("/users/")

        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 2

        usernames = [u["username"] for u in data]
        assert "existinguser" in usernames
        assert "existingadmin" in usernames

    async def test_get_all_users_as_student_forbidden(
        self, auth_client: AsyncClient
    ):  # ← ИСПРАВЛЕНО: auth_client
        """Студент не может получить список всех пользователей"""
        response = await auth_client.get("/users/")

        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 403

    async def test_get_user_by_id_as_admin(
        self, admin_client: AsyncClient, test_user
    ):  # ← ИСПРАВЛЕНО: admin_client
        """Админ получает пользователя по ID"""
        response = await admin_client.get(f"/users/{test_user.id}")

        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200

        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

    async def test_get_user_by_id_not_found(
        self, admin_client: AsyncClient
    ):  # ← ИСПРАВЛЕНО: admin_client
        """Запрос несуществующего пользователя"""
        response = await admin_client.get("/users/99999")

        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 404

    async def test_get_user_by_id_as_student_forbidden(
        self, auth_client: AsyncClient, test_user
    ):  # ← ЭТОТ ТЕСТ УЖЕ ЕСТЬ
        """Студент не может получить пользователя по ID"""
        response = await auth_client.get(f"/users/{test_user.id}")
        assert response.status_code == 403
