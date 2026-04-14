from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from src.core.database import get_db  # ← ДОБАВЬТЕ ЭТОТ ИМПОРТ!
from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from src.crud.user import crud_user
from src.schemas.user import UserCreate, UserResponse
from src.schemas.token import Token, RefreshTokenRequest

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверяем, нет ли пользователя с таким username или email
    db_user = await crud_user.get_by_username(db, user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = await crud_user.get_by_email(db, user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создаем пользователя
    user = await crud_user.create(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Вход пользователя"""
    user = await crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Обновляем время последнего входа
    from datetime import datetime

    user.last_login = datetime.utcnow()
    await db.commit()

    # Создаем токены
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """Обновление access токена"""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = await crud_user.get_by_username(db, username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Создаем новые токены
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout():
    """Выход пользователя"""
    # В реальной системе нужно добавить токен в blacklist
    return {"message": "Successfully logged out"}
