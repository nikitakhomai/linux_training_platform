import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from src.core.security import verify_token, get_current_user, get_current_admin_user

pytestmark = pytest.mark.asyncio


class TestSecurity:
    """Тесты безопасности"""

    # @patch("src.core.security.httpx.AsyncClient")
    # async def test_verify_token_valid(self, mock_client):
    #     """Проверка валидного токена"""
    #     # Мокаем успешный ответ
    #     mock_response = AsyncMock()
    #     mock_response.status_code = 200
    #     # ВАЖНО: json должен быть AsyncMock, возвращающий словарь
    #     mock_response.json = AsyncMock(
    #         return_value={
    #             "id": 1,
    #             "username": "testuser",
    #             "role": "student",
    #         }
    #     )
    #
    #     # Мокаем клиент
    #     mock_instance = AsyncMock()
    #     mock_instance.__aenter__.return_value.get.return_value = mock_response
    #     mock_client.return_value = mock_instance
    #
    #     result = await verify_token("valid_token")
    #
    #     assert result is not None
    #     assert result["username"] == "testuser"
    #     assert result["role"] == "student"

    @patch("src.core.security.httpx.AsyncClient")
    async def test_verify_token_invalid(self, mock_client):
        """Проверка невалидного токена"""
        mock_response = AsyncMock()
        mock_response.status_code = 401

        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value = mock_instance

        result = await verify_token("invalid_token")
        assert result is None

    @patch("src.core.security.httpx.AsyncClient")
    async def test_verify_token_error(self, mock_client):
        """Проверка при ошибке сети"""
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value.get.side_effect = Exception(
            "Connection error"
        )
        mock_client.return_value = mock_instance

        result = await verify_token("token")
        assert result is None

    async def test_get_current_user_valid(self):
        """Получение текущего пользователя с валидным токеном"""
        with patch(
            "src.core.security.verify_token",
            return_value={"id": 1, "username": "testuser", "role": "student"},
        ):
            mock_credentials = AsyncMock()
            mock_credentials.credentials = "valid_token"

            user = await get_current_user(mock_credentials)

            assert user is not None
            assert user["username"] == "testuser"
            assert user["role"] == "student"

    async def test_get_current_user_invalid(self):
        """Получение текущего пользователя с невалидным токеном"""
        with patch("src.core.security.verify_token", return_value=None):
            mock_credentials = AsyncMock()
            mock_credentials.credentials = "invalid_token"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == 401

    async def test_get_current_user_no_credentials(self):
        """Получение текущего пользователя без токена"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None)
        assert exc_info.value.status_code == 401

    async def test_get_current_admin_user_valid(self):
        """Получение текущего администратора с валидным токеном"""
        with patch(
            "src.core.security.get_current_user",
            return_value={"id": 1, "username": "admin", "role": "admin"},
        ):
            mock_credentials = AsyncMock()
            mock_credentials.credentials = "admin_token"

            user = await get_current_admin_user(mock_credentials)
            assert user is not None
            assert user["role"] == "admin"

    async def test_get_current_admin_user_not_admin(self):
        """Попытка получить админа с ролью студента"""
        with patch(
            "src.core.security.get_current_user",
            return_value={"id": 1, "username": "student", "role": "student"},
        ):
            mock_credentials = AsyncMock()
            mock_credentials.credentials = "student_token"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_admin_user(mock_credentials)

            assert exc_info.value.status_code == 403
