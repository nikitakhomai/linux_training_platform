import pytest
import sys
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


class TestCategoriesAPI:
    """Тесты для API категорий"""

    async def test_get_categories_empty(self, client: AsyncClient):
        """Получение пустого списка категорий"""
        response = await client.get("/categories/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_category_as_student_forbidden(self, client: AsyncClient):
        """Студент не может создавать категории"""
        category_data = {
            "name": "Network Security",
            "description": "Test",
            "icon": "🌐",
        }

        response = await client.post("/categories/", json=category_data)

        # ОТЛАДКА
        print("\n=== DEBUG CREATE CATEGORY (STUDENT) ===", file=sys.stderr)
        print(f"Status code: {response.status_code}", file=sys.stderr)
        print(f"Response body: {response.text}", file=sys.stderr)
        print("======================================\n", file=sys.stderr)

        assert response.status_code == 403  # Forbidden

    async def test_get_categories_with_data(
        self, admin_client: AsyncClient, test_category
    ):
        """Получение списка категорий с данными"""
        response = await admin_client.get("/categories/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1

        # Проверяем, что наша тестовая категория есть в списке
        category_names = [c["name"] for c in data]
        assert test_category.name in category_names

    async def test_get_category_by_id(self, client: AsyncClient, test_category):
        """Получение категории по ID"""
        response = await client.get(f"/categories/{test_category.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == test_category.name
        assert data["description"] == test_category.description

    async def test_get_category_not_found(self, client: AsyncClient):
        """Получение несуществующей категории"""
        response = await client.get("/categories/99999")
        assert response.status_code == 404

    async def test_update_category_as_admin(
        self, admin_client: AsyncClient, test_category
    ):
        """Обновление категории администратором"""
        update_data = {
            "name": "Updated Category Name",
            "description": "Updated Description",
        }

        response = await admin_client.put(
            f"/categories/{test_category.id}", json=update_data
        )

        # ОТЛАДКА
        print("\n=== DEBUG UPDATE CATEGORY ===", file=sys.stderr)
        print(f"Status code: {response.status_code}", file=sys.stderr)
        print(f"Response body: {response.text}", file=sys.stderr)
        print("=============================\n", file=sys.stderr)

        assert response.status_code == 200

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        # Поля, которые не обновлялись, должны остаться
        assert data["icon"] == test_category.icon

    async def test_update_category_as_student_forbidden(
        self, client: AsyncClient, test_category
    ):
        """Студент не может обновлять категории"""
        update_data = {"name": "Hacked Name"}

        response = await client.put(f"/categories/{test_category.id}", json=update_data)
        assert response.status_code == 403

    async def test_delete_category_as_admin(
        self, admin_client: AsyncClient, test_category
    ):
        """Удаление категории администратором"""
        response = await admin_client.delete(f"/categories/{test_category.id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Category deleted successfully"

        # Проверяем, что категория действительно удалена
        get_response = await admin_client.get(f"/categories/{test_category.id}")
        assert get_response.status_code == 404

    async def test_delete_category_as_student_forbidden(
        self, client: AsyncClient, test_category
    ):
        """Студент не может удалять категории"""
        response = await client.delete(f"/categories/{test_category.id}")
        assert response.status_code == 403
