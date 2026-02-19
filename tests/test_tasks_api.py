import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.test_app import app
from app.models.models import Task, TaskCreate, TaskUpdate, TaskStatus, Priority


@pytest.mark.asyncio
class TestTasksEndpoints:
    """Integration tests for task API endpoints."""

    async def test_create_task_success(self, client: TestClient):
        """Test successful task creation returns 201 with Task object."""
        mock_task = MagicMock()
        mock_task.id = "task_123"
        mock_task.title = "Test Task"
        mock_task.description = "Test Description"
        mock_task.priority = Priority.MEDIUM
        mock_task.status = TaskStatus.OPEN
        mock_task.list_id = "list_456"
        mock_task.assignee_id = None
        mock_task.due_date = None
        mock_task.tags = []
        mock_task.created_at = datetime.utcnow()
        mock_task.updated_at = datetime.utcnow()

        with patch('app.services.task_service.create_task', return_value=mock_task):
            response = await client.post(
                "/api/v1/tasks",
                json=mock_task.__dict__
            )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Task"

    async def test_create_task_invalid_data(self, client: TestClient):
        """Test task creation with invalid data returns 422."""
        mock_user = MagicMock()
        mock_user.id = "user_123"

        with patch('app.api.dependencies.get_current_user', return_value=mock_user):
            response = await client.post(
                "/api/v1/tasks",
                json={
                    "title": "Test Task"
                },
                headers={"Authorization": "Bearer valid_token"}
            )

        assert response.status_code == 422

    async def test_get_task_by_id_success(self, client: TestClient):
        """Test retrieving task by ID returns 200 with Task object."""
        mock_task = MagicMock()
        mock_task.id = "task_123"
        mock_task.title = "Test Task"
        mock_task.description = "Test Description"
        mock_task.priority = Priority.MEDIUM
        mock_task.status = TaskStatus.OPEN
        mock_task.list_id = "list_456"
        mock_task.assignee_id = None
        mock_task.due_date = None
        mock_task.tags = []
        mock_task.created_at = datetime.utcnow()
        mock_task.updated_at = datetime.utcnow()

        with patch('app.services.task_service.get_task_by_id', return_value=mock_task):
            response = await client.get(f"/api/v1/tasks/task_123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "task_123"
        assert data["title"] == "Test Task"

    async def test_get_task_by_id_not_found(self, client: TestClient):
        """Test retrieving non-existent task returns 404."""
        with patch('app.services.task_service.get_task_by_id', return_value=None):
            response = await client.get("/api/v1/tasks/non_existent_task")

        assert response.status_code == 404

    async def test_list_tasks_success(self, client: TestClient):
        """Test listing tasks returns 200 with list of tasks."""
        mock_tasks = [
            MagicMock(id="task_001", title="Task 1", status=TaskStatus.OPEN.value, list_id="list_123"),
            MagicMock(id="task_002", title="Task 2", status=TaskStatus.IN_PROGRESS.value, list_id="list_123"),
            MagicMock(id="task_003", title="Task 3", status=TaskStatus.DONE.value, list_id="list_123"),
        ]

        with patch('app.services.task_service.list_tasks', return_value=mock_tasks):
            response = await client.get("/api/v1/tasks?list_id=list_123")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_list_tasks_with_filters(self, client: TestClient):
        """Test listing tasks with status filter."""
        mock_tasks = [
            MagicMock(id="task_001", title="Task 1", status=TaskStatus.OPEN.value, list_id="list_123"),
            MagicMock(id="task_002", title="Task 2", status=TaskStatus.IN_PROGRESS.value, list_id="list_123"),
        ]

        with patch('app.services.task_service.list_tasks', return_value=mock_tasks):
            response = await client.get("/api/v1/tasks?list_id=list_123&status=OPEN")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert all(t["status"] == TaskStatus.OPEN.value for t in data)

    async def test_list_tasks_with_sorting(self, client: TestClient):
        """Test listing tasks with sort parameter."""
        mock_tasks = [
            MagicMock(id="task_001", title="Task 1", created_at="2026-01-15T00:00:00", list_id="list_123"),
            MagicMock(id="task_002", title="Task 2", created_at="2026-01-16T00:00:00", list_id="list_123"),
        ]

        with patch('app.services.task_service.list_tasks', return_value=mock_tasks):
            response = await client.get("/api/v1/tasks?list_id=list_123&sort=desc")

        assert response.status_code == 200
        data = response.json()
        assert data[0].title == "Task 2"
        assert data[1].title == "Task 1"

    async def test_update_task_success(self, client: TestClient):
        """Test updating task returns 200."""
        mock_task = MagicMock()
        mock_task.id = "task_123"
        mock_task.title = "Updated Task"
        mock_task.description = "Updated Description"

        with patch('app.services.task_service.get_task_by_id', return_value=mock_task):
            response = await client.put(
                f"/api/v1/tasks/task_123",
                json={"title": "Updated Task", "description": "Updated Description"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"

    async def test_update_task_not_found(self, client: TestClient):
        """Test updating non-existent task returns 404."""
        with patch('app.services.task_service.get_task_by_id', return_value=None):
            response = await client.put(
                "/api/v1/tasks/non_existent",
                json={"title": "Updated Task"}
            )

        assert response.status_code == 404

    async def test_delete_task_success(self, client: TestClient):
        """Test deleting task returns 204."""
        with patch('app.services.task_service.delete_task', return_value=True):
            response = await client.delete("/api/v1/tasks/task_123")

        assert response.status_code == 204

    async def test_delete_task_not_found(self, client: TestClient):
        """Test deleting non-existent task returns 404."""
        with patch('app.services.task_service.delete_task', return_value=False):
            response = await client.delete("/api/v1/tasks/non_existent")

        assert response.status_code == 404

    async def test_unauthenticated_access_post(self, client: TestClient):
        """Test POST without authentication returns 401."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "list_id": "list_123"}
        )

        assert response.status_code == 401

    async def test_unauthenticated_access_get(self, client: TestClient):
        """Test GET without authentication returns 401."""
        response = await client.get("/api/v1/tasks/task_123")

        assert response.status_code == 401

    async def test_unauthenticated_access_list(self, client: TestClient):
        """Test GET list without authentication returns 401."""
        response = await client.get("/api/v1/tasks")

        assert response.status_code == 401

    async def test_unauthenticated_access_put(self, client: TestClient):
        """Test PUT without authentication returns 401."""
        response = await client.put(
                "/api/v1/tasks/task_123",
                json={"title": "Updated Task"}
        )

        assert response.stat
