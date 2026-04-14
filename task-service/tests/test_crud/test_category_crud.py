import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.category import crud_category
from src.schemas.category import CategoryCreate, CategoryUpdate

pytestmark = pytest.mark.asyncio

class TestCategoryCRUD:
    """Тесты CRUD операций для категорий"""
    
    async def test_create_category(self, db_session: AsyncSession):
        """Создание категории"""
        category_in = CategoryCreate(
            name="Test CRUD Category",
            description="Created by CRUD test",
            icon="🧪"
        )
        
        category = await crud_category.create(db_session, category_in)
        
        assert category.id is not None
        assert category.name == category_in.name
        assert category.description == category_in.description
        assert category.icon == category_in.icon
    
    async def test_get_category(self, db_session: AsyncSession, test_category):
        """Получение категории по ID"""
        category = await crud_category.get(db_session, test_category.id)
        
        assert category is not None
        assert category.id == test_category.id
        assert category.name == test_category.name
    
    async def test_get_category_not_found(self, db_session: AsyncSession):
        """Получение несуществующей категории"""
        category = await crud_category.get(db_session, 99999)
        assert category is None
    
    async def test_get_multi_categories(self, db_session: AsyncSession, test_category):
        """Получение списка категорий"""
        categories = await crud_category.get_multi(db_session)
        
        assert len(categories) >= 1
        assert test_category.id in [c.id for c in categories]
    
    async def test_update_category(self, db_session: AsyncSession, test_category):
        """Обновление категории"""
        update_data = CategoryUpdate(
            name="Updated CRUD Name",
            description="Updated description"
        )
        
        updated = await crud_category.update(db_session, test_category.id, update_data)
        
        assert updated is not None
        assert updated.name == update_data.name
        assert updated.description == update_data.description
        # Поля, которые не обновлялись, должны остаться
        assert updated.icon == test_category.icon
    
    async def test_update_category_no_changes(self, db_session: AsyncSession, test_category):
        """Обновление без изменений"""
        update_data = CategoryUpdate()
        
        updated = await crud_category.update(db_session, test_category.id, update_data)
        
        assert updated is not None
        assert updated.name == test_category.name
        assert updated.description == test_category.description
    
    async def test_delete_category(self, db_session: AsyncSession, test_category):
        """Удаление категории"""
        # Создаем отдельную категорию для удаления
        category_in = CategoryCreate(name="To Delete", description="Will be deleted")
        category = await crud_category.create(db_session, category_in)
        
        # Удаляем
        result = await crud_category.delete(db_session, category.id)
        assert result is True
        
        # Проверяем, что удалена
        deleted = await crud_category.get(db_session, category.id)
        assert deleted is None
    
    async def test_delete_category_not_found(self, db_session: AsyncSession):
        """Удаление несуществующей категории"""
        result = await crud_category.delete(db_session, 99999)
        assert result is False
