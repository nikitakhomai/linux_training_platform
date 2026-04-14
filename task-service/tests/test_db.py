import pytest
from sqlalchemy import text
from src.core.database import Base
from src.models.category import Category
from src.models.course import Course
from src.models.task import Task

pytestmark = pytest.mark.asyncio

async def test_tables_exist(db_session):
    """Проверяем, что таблицы действительно создаются"""
    # Проверяем, что можем выполнить запрос к categories
    result = await db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = result.fetchall()
    print(f"\nТаблицы в БД: {[t[0] for t in tables]}")
    
    # Должны быть таблицы categories, courses, tasks
    table_names = [t[0] for t in tables]
    assert "categories" in table_names
    assert "courses" in table_names
    assert "tasks" in table_names
