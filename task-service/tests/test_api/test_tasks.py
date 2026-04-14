import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

class TestTasksAPI:
    """Тесты для API заданий"""
    
    async def test_get_tasks_empty(self, client: AsyncClient):
        """Получение пустого списка заданий"""
        response = await client.get("/tasks/")
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_create_task_as_admin(self, admin_client: AsyncClient, test_course):
        """Создание задания администратором"""
        task_data = {
            "title": "SSH Hardening",
            "description": "Настройте безопасный SSH доступ",
            "task_type": "hardening",
            "course_id": test_course.id,
            "order_in_course": 1,
            "docker_image": "ubuntu:22.04",
            "points": 50,
            "difficulty": "easy",
            "estimated_time_minutes": 20,
            "is_published": True
        }
        
        response = await admin_client.post("/tasks/", json=task_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["task_type"] == task_data["task_type"]
        assert data["course_id"] == test_course.id
        assert data["docker_image"] == task_data["docker_image"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_task_as_student_forbidden(self, client: AsyncClient, test_course):
        """Студент не может создавать задания"""
        task_data = {
            "title": "Test Task",
            "description": "Test",
            "task_type": "hardening",
            "docker_image": "ubuntu:22.04",
            "points": 10,
            "difficulty": "easy",
            "estimated_time_minutes": 5
        }
        
        response = await client.post("/tasks/", json=task_data)
        assert response.status_code == 403
    
    async def test_get_tasks_filter_by_course(self, client: AsyncClient, test_task, test_course):
        """Фильтрация заданий по курсу"""
        response = await client.get(f"/tasks/?course_id={test_course.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        
        # Все задания должны быть из указанного курса
        for task in data:
            assert task["course_id"] == test_course.id
    
    async def test_get_task_by_id(self, client: AsyncClient, test_task):
        """Получение задания по ID"""
        response = await client.get(f"/tasks/{test_task.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title
        assert data["description"] == test_task.description
    
    async def test_get_task_not_found(self, client: AsyncClient):
        """Получение несуществующего задания"""
        response = await client.get("/tasks/99999")
        assert response.status_code == 404
    
    async def test_update_task_as_admin(self, admin_client: AsyncClient, test_task):
        """Обновление задания администратором"""
        update_data = {
            "title": "Updated Task Title",
            "points": 100,
            "difficulty": "hard"
        }
        
        response = await admin_client.put(f"/tasks/{test_task.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["points"] == update_data["points"]
        assert data["difficulty"] == update_data["difficulty"]
    
    async def test_update_task_as_student_forbidden(self, client: AsyncClient, test_task):
        """Студент не может обновлять задания"""
        update_data = {"title": "Hacked Title"}
        
        response = await client.put(f"/tasks/{test_task.id}", json=update_data)
        assert response.status_code == 403
    
    async def test_delete_task_as_admin(self, admin_client: AsyncClient, test_task):
        """Удаление задания администратором"""
        response = await admin_client.delete(f"/tasks/{test_task.id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Task deleted successfully"
        
        # Проверяем, что задание действительно удалено
        get_response = await admin_client.get(f"/tasks/{test_task.id}")
        assert get_response.status_code == 404
    
    async def test_task_ordering_in_course(self, admin_client: AsyncClient, test_course):
        """Проверка сортировки заданий в курсе"""
        # Создаем несколько заданий с разным порядком
        task1_data = {
            "title": "Task 1",
            "description": "First task",
            "task_type": "hardening",
            "course_id": test_course.id,
            "order_in_course": 2,
            "docker_image": "ubuntu:22.04",
            "points": 10,
            "difficulty": "easy",
            "estimated_time_minutes": 10,
            "is_published": True
        }
        task2_data = {
            "title": "Task 2",
            "description": "Second task",
            "task_type": "hardening",
            "course_id": test_course.id,
            "order_in_course": 1,
            "docker_image": "ubuntu:22.04",
            "points": 10,
            "difficulty": "easy",
            "estimated_time_minutes": 10,
            "is_published": True
        }
        
        await admin_client.post("/tasks/", json=task1_data)
        await admin_client.post("/tasks/", json=task2_data)
        
        # Получаем задания курса
        response = await admin_client.get(f"/tasks/?course_id={test_course.id}")
        tasks = response.json()
        
        # Проверяем, что они отсортированы по order_in_course
        orders = [t["order_in_course"] for t in tasks[-2:]]  # Берем только новые
        assert orders == sorted(orders)
