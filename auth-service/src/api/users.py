from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.core.database import get_db
from src.crud.user import crud_user
from src.schemas.user import UserResponse
from src.core.security import decode_token
from fastapi.security import OAuth2PasswordBearer
from src.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Получить текущего пользователя из токена"""
    print(f"\n=== GET CURRENT USER ===")
    print(f"Token received: {token[:20] if token else 'None'}...")

    payload = decode_token(token)
    if not payload:
        print("Token decode failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    print(f"Token payload: {payload}")

    username = payload.get("sub")
    if not username:
        print("No username in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = await crud_user.get_by_username(db, username)
    if not user:
        print(f"User not found: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    print(f"User found: {user.username}")
    print("========================\n")
    return user


async def get_current_active_admin(
    current_user: UserResponse = Depends(get_current_user),
):
    """Проверка, что пользователь - администратор"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_admin),
):
    """Получить список пользователей (только для админов)"""
    from sqlalchemy import select

    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_admin),
):
    """Получить пользователя по ID (только для админов)"""
    user = await crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
