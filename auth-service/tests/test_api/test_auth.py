import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


class TestAuthAPI:
    """Тесты для API аутентификации"""

    async def test_register_success(self, client: AsyncClient):
        """Успешная регистрация пользователя"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "role": "student",
        }

        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["role"] == user_data["role"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Пароль не должен возвращаться

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Регистрация с существующим username"""
        user_data = {
            "username": "existinguser",  # Уже существует из test_user
            "email": "another@example.com",
            "password": "password123",
            "full_name": "Another User",
            "role": "student",
        }

        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.text

    async def test_login_success(self, client: AsyncClient, test_user):
        """Успешный вход"""
        login_data = {"username": "existinguser", "password": "password123"}

        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Регистрация с существующим email"""
        user_data = {
            "username": "anotheruser",
            "email": "existing@example.com",  # Уже существует из test_user
            "password": "password123",
            "full_name": "Another User",
            "role": "student",
        }

        response = await client.post("/auth/register", json=user_data)

        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 400
        assert "Email already registered" in response.text

    async def test_register_password_too_short(self, client: AsyncClient):
        """Регистрация с коротким паролем"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "123",  # Слишком короткий
            "full_name": "New User",
            "role": "student",
        }

        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Вход с неверным паролем"""
        login_data = {"username": "existinguser", "password": "wrongpassword"}

        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.text

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Вход с несуществующим пользователем"""
        login_data = {"username": "nonexistent", "password": "password123"}

        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 401

    async def test_refresh_token_success(self, client: AsyncClient, test_user):
        """Успешное обновление токена"""
        # Сначала логинимся
        login_data = {"username": "existinguser", "password": "password123"}
        login_response = await client.post("/auth/login", data=login_data)

        print(f"Login status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")

        assert login_response.status_code == 200
        tokens = login_response.json()

        # Проверяем, что есть refresh_token
        assert "refresh_token" in tokens, "refresh_token not in response"
        refresh_token = tokens["refresh_token"]

        # Обновляем токен
        response = await client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )

        print(f"\nRefresh status: {response.status_code}")
        print(f"Refresh response: {response.text}")

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Обновление с невалидным refresh token"""
        response = await client.post(
            "/auth/refresh", json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401

    async def test_logout(self, auth_client: AsyncClient):
        """Выход из системы"""
        response = await auth_client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
