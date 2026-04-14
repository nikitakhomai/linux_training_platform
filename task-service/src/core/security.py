from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from src.core.config import settings

security = HTTPBearer()


async def verify_token(token: str) -> dict | None:
    """Проверка токена через auth-service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )

            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Получить текущего пользователя по токену"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    token = credentials.credentials
    user_data = await verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    return user_data


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Получить текущего пользователя, если он администратор"""
    user_data = await get_current_user(credentials)

    if user_data.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # ← ИСПРАВЛЕНО!
            detail="Not enough permissions",
        )

    return user_data
