import pytest
from datetime import datetime, timedelta
from jose import jwt
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.core.config import settings

pytestmark = pytest.mark.asyncio


class TestSecurity:
    """Тесты безопасности (JWT, хэширование)"""

    def test_password_hashing(self):
        """Тест хэширования пароля"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Создание access token"""
        data = {"sub": "testuser", "role": "student"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

        # Декодируем и проверяем
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "testuser"
        assert payload["role"] == "student"
        assert "exp" in payload

    def test_create_access_token_with_expiry(self):
        """Создание access token с кастомным временем жизни"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "testuser"

    def test_create_refresh_token(self):
        """Создание refresh token"""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_decode_token_valid(self):
        """Декодирование валидного токена"""
        data = {"sub": "testuser", "role": "student"}
        token = create_access_token(data)

        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "student"

    def test_decode_token_invalid(self):
        """Декодирование невалидного токена"""
        payload = decode_token("invalid.token.here")
        assert payload is None

    def test_decode_token_expired(self):
        """Декодирование просроченного токена"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Уже просрочен
        token = create_access_token(data, expires_delta)

        payload = decode_token(token)
        assert payload is None
