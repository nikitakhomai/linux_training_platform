import pytest
import sys
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestCoursesAPI:
    """Тесты для API курсов"""

    async def test_get_courses_empty(self, client: AsyncClient):
        """Получение пустого списка курсов"""
        response = await client.get("/courses/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_course_as_admin(
        self, admin_client: AsyncClient, test_category
    ):
        """Создание курса администратором"""
        import json
        import sys

        course_data = {
            "title": "Linux Security Basics",
            "description": "Введение в безопасность Linux",
            "difficulty": "beginner",
            "category_id": test_category.id,
            "order": 1,
            "is_published": True,
            "estimated_time_minutes": 120,
        }

        # Отладка клиента
        print("\n=== CLIENT DEBUG ===", file=sys.stderr)
        print(f"Headers: {admin_client.headers}", file=sys.stderr)
        print(f"Base URL: {admin_client.base_url}", file=sys.stderr)
        print("====================\n", file=sys.stderr)

        # Отладка запроса
        print("=== REQUEST DEBUG ===", file=sys.stderr)
        print(f"URL: /courses/", file=sys.stderr)
        print(f"Method: POST", file=sys.stderr)
        print(f"Data: {json.dumps(course_data, indent=2)}", file=sys.stderr)
        print("====================\n", file=sys.stderr)

        # Отправка запроса
        response = await admin_client.post("/courses/", json=course_data)

        # Отладка ответа
        print("=== RESPONSE DEBUG ===", file=sys.stderr)
        print(f"Status: {response.status_code}", file=sys.stderr)
        print(f"Headers: {dict(response.headers)}", file=sys.stderr)
        print(f"Body: {response.text}", file=sys.stderr)
        print("=====================\n", file=sys.stderr)

        assert response.status_code == 200

    async def test_create_course_as_student_forbidden(
        self, client: AsyncClient, test_category
    ):
        """Студент не может создавать курсы"""
        course_data = {
            "title": "Test Course",
            "description": "Test",
            "difficulty": "beginner",
            "category_id": test_category.id,
            "estimated_time_minutes": 60,
        }

        response = await client.post("/courses/", json=course_data)
        assert response.status_code == 403

    async def test_get_courses_filter_by_category(
        self, client: AsyncClient, test_course, test_category
    ):
        """Фильтрация курсов по категории"""
        response = await client.get(f"/courses/?category_id={test_category.id}")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1

        # Все курсы должны быть из указанной категории
        for course in data:
            assert course["category_id"] == test_category.id

    async def test_get_courses_filter_published(
        self, client: AsyncClient, admin_client: AsyncClient
    ):
        """Фильтрация по статусу публикации"""
        # Создаем опубликованный курс
        published_data = {
            "title": "Published Course",
            "description": "Test",
            "difficulty": "beginner",
            "is_published": True,
            "estimated_time_minutes": 60,
        }
        await admin_client.post("/courses/", json=published_data)

        # Создаем неопубликованный курс
        unpublished_data = {
            "title": "Unpublished Course",
            "description": "Test",
            "difficulty": "beginner",
            "is_published": False,
            "estimated_time_minutes": 60,
        }
        await admin_client.post("/courses/", json=unpublished_data)

        # Обычный пользователь видит только опубликованные
        response = await client.get("/courses/?is_published=true")
        assert response.status_code == 200

        for course in response.json():
            assert course["is_published"] is True

    # async def test_get_course_by_id(self, client: AsyncClient, test_course):
    #     """Получение курса по ID"""
    #     response = await client.get(f"/courses/{test_course.id}")
    #     assert response.status_code == 200
    #
    #     data = response.json()
    #     assert data["id"] == test_course.id
    #     assert data["title"] == test_course.title
    #     assert "tasks" in data  # Проверяем, что связанные задачи включены

    async def test_update_course_as_admin(self, admin_client: AsyncClient, test_course):
        """Обновление курса администратором"""
        update_data = {"title": "Updated Course Title", "difficulty": "advanced"}

        response = await admin_client.put(
            f"/courses/{test_course.id}", json=update_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["difficulty"] == update_data["difficulty"]
        # Поля, которые не обновлялись, должны остаться
        assert data["description"] == test_course.description

    async def test_delete_course_as_admin(self, admin_client: AsyncClient, test_course):
        """Удаление курса администратором"""
        response = await admin_client.delete(f"/courses/{test_course.id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Course deleted successfully"

        # Проверяем, что курс действительно удален
        get_response = await admin_client.get(f"/courses/{test_course.id}")
        assert get_response.status_code == 404
