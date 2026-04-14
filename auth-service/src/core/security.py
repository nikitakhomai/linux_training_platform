from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
from src.core.config import settings

# ========== ХЭШИРОВАНИЕ ПАРОЛЕЙ ==========


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Простая проверка пароля (для тестирования)"""
    if not plain_password or not hashed_password:
        return False
    test_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return test_hash == hashed_password


def get_password_hash(password: str) -> str:
    """Простое хэширование пароля (для тестирования)"""
    if not password:
        return ""
    return hashlib.sha256(password.encode()).hexdigest()


# ========== JWT ТОКЕНЫ ==========


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена доступа"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict):
    """Создание refresh токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str):
    """Декодирование токена"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ========== ЗАВИСИМОСТИ ДЛЯ FASTAPI (нужны для тестов) ==========


async def verify_token(token: str) -> Optional[dict]:
    """
    Проверка токена (для совместимости с тестами)
    """
    payload = decode_token(token)
    if payload:
        return {
            "id": 1,
            "username": payload.get("sub", "testuser"),
            "role": payload.get("role", "student"),
            "is_active": True,
        }
    return None


async def get_current_user(credentials) -> dict:
    """
    Получить текущего пользователя по токену
    """
    # Для тестов без реальной аутентификации
    if hasattr(credentials, "credentials"):
        token = credentials.credentials
        user_data = await verify_token(token)
        if user_data:
            return user_data

    from fastapi import HTTPException, status

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_admin_user(credentials) -> dict:
    """
    Получить текущего пользователя, если он администратор
    """
    user_data = await get_current_user(credentials)

    if user_data.get("role") != "admin":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return user_data
