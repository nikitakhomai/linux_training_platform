import pytest
from sqlalchemy import text
from src.core.database import Base
from src.models.user import User

pytestmark = pytest.mark.asyncio


async def test_tables_exist(db_session):
    """Проверяем, что таблицы действительно создаются"""
    # Проверяем, какие таблицы есть
    result = await db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table'")
    )
    tables = result.fetchall()
    print(f"\nТаблицы в БД: {[t[0] for t in tables]}")

    # Проверяем структуру таблицы users
    result = await db_session.execute(text("PRAGMA table_info(users)"))
    columns = result.fetchall()
    print(f"Колонки в users: {[c[1] for c in columns]}")

    # Должны быть таблицы
    table_names = [t[0] for t in tables]
    assert "users" in table_names
