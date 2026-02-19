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
        # Arrange
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

        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": Priority.MEDIUM,
            "status": TaskStatus.OPEN,
            "list_id": "list_456",
            "assignee_id": None,
            "due_date": None,
            "tags": []
        }

        with patch('app.api.tasks.create_task', return_value=mock_task):
            response = client.post(
                "/api/v1/tasks",
                json=task_data
            )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["list_id"] == "list_456"

    async def test_create_task_invalid_data(self, client: TestClient):
        """Test task creation with invalid data returns 422."""
        # Act - Missing required list_id field
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task"
                # Missing list_id - required field
            }
        )

        # Assert
        assert response.status_code == 422

    async def test_get_task_by_id_success(self, client: TestClient):
        """Test getting task by valid ID returns 200 with Task object."""
        # Arrange
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

        with patch('app.api.tasks.get_task_by_id', return_value=mock_task):
            # Act
            response = client.get(
                "/api/v1/tasks/task_123"
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "task_123"
        assert data["title"] == "Test Task"

    async def test_get_task_by_id_not_found(self, client: TestClient):
        """Test getting task by non-existent ID returns 404."""
        # Arrange
        with patch('app.api.tasks.get_task_by_id', return_value=None):
            # Act
            response = client.get(
                "/api/v1/tasks/nonexistent_id"
            )

        # Assert
        assert response.status_code == 404

    async def test_list_tasks_success(self, client: TestClient):
        """Test listing tasks returns 200 with list of Task objects."""
        # Arrange
        mock_task1 = MagicMock()
        mock_task1.id = "task_123"
        mock_task1.title = "Task 1"
        mock_task1.list_id = "list_456"
        mock_task1.priority = Priority.MEDIUM
        mock_task1.status = TaskStatus.OPEN
        mock_task1.description = None
        mock_task1.assignee_id = None
        mock_task1.due_date = None
        mock_task1.tags = []
        mock_task1.created_at = datetime.utcnow()
        mock_task1.updated_at = datetime.utcnow()

        mock_task2 = MagicMock()
        mock_task2.id = "task_789"
        mock_task2.title = "Task 2"
        mock_task2.list_id = "list_456"
        mock_task2.priority = Priority.HIGH
        mock_task2.status = TaskStatus.IN_PROGRESS
        mock_task2.description = None
        mock_task2.assignee_id = None
        mock_task2.due_date = None
        mock_task2.tags = []
        mock_task2.created_at = datetime.utcnow()
        mock_task2.updated_at = datetime.utcnow()

        with patch('app.api.tasks.list_tasks', return_value=[mock_task1, mock_task2]):
            # Act
            response = client.get(
                "/api/v1/tasks?list_id=list_456"
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"

    async def test_list_tasks_with_filters(self, client: TestClient):
        """Test listing tasks with status filter returns filtered list."""
        # Arrange
        mock_task = MagicMock()
        mock_task.id = "task_123"
        mock_task.title = "Open Task"
        mock_task.list_id = "list_456"
        mock_task.priority = Priority.MEDIUM
        mock_task.status = TaskStatus.OPEN
        mock_task.description = None
        mock_task.assignee_id = None
        mock_task.due_date = None
        mock_task.tags = []
        mock_task.created_at = datetime.utcnow()
        mock_task.updated_at = datetime.utcnow()

        with patch('app.api.tasks.list_tasks', return_value=[mock_task]):
            # Act
            response = client.get(
                "/api/v1/tasks?list_id=list_456&status=OPEN"
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["status"] == "OPEN"

    async def test_list_tasks_with_sorting(self, client: TestClient):
        """Test listing tasks with sort param returns sorted list."""
        # Arrange
        mock_task1 = MagicMock()
        mock_task1.id = "task_1"
        mock_task1.title = "Task A"
        mock_task1.list_id = "list_456"
        mock_task1.priority = Priority.LOW
        mock_task1.status = TaskStatus.OPEN
        mock_task1.description = None
        mock_task1.assignee_id = None
        mock_task1.due_date = None
        mock_task1.tags = []
        mock_task1.created_at = datetime.utcnow()
        mock_task1.updated_at = datetime.utcnow()

        mock_task2 = MagicMock()
        mock_task2.id = "task_2"
        mock_task2.title = "Task B"
        mock_task2.list_id = "list_456"
        mock_task2.priority = Priority.HIGH
        mock_task2.status = TaskStatus.OPEN
        mock_task2.description = None
        mock_task2.assignee_id = None
        mock_task2.due_date = None
        mock_task2.tags = []
        mock_task2.created_at = datetime.utcnow()
        mock_task2.updated_at = datetime.utcnow()

        with patch('app.api.tasks.list_tasks', return_value=[mock_task2, mock_task1]):
            # Act
            response = client.get(
                "/api/v1/tasks?list_id=list_456&sort=priority"
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    async def test_update_task_success(self, client: TestClient):
        """Test updating task with valid data returns 200 with updated Task."""
        # Arrange
        mock_updated_task = MagicMock()
        mock_updated_task.id = "task_123"
        mock_updated_task.title = "Updated Task"
        mock_updated_task.description = "Updated Description"
        mock_updated_task.priority = Priority.HIGH
        mock_updated_task.status = TaskStatus.IN_PROGRESS
        mock_updated_task.list_id = "list_456"
        mock_updated_task.assignee_id = "user_789"
        mock_updated_task.due_date = None
        mock_updated_task.tags = ["urgent"]
        mock_updated_task.created_at = datetime.utcnow()
        mock_updated_task.updated_at = datetime.utcnow()

        with patch('app.api.tasks.update_task', return_value=mock_updated_task):
            # Act
            response = client.put(
                "/api/v1/tasks/task_123",
                json={
                    "title": "Updated Task",
                    "description": "Updated Description",
                    "priority": 3,
                    "status": "IN_PROGRESS"
                }
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated Description"

    async def test_update_task_not_found(self, client: TestClient):
        """Test updating non-existent task returns 404."""
        # Arrange
        with patch('app.api.tasks.update_task', return_value=None):
            # Act
            response = client.put(
                "/api/v1/tasks/nonexistent_id",
                json={"title": "Updated Task"}
            )

        # Assert
        assert response.status_code == 404

    async def test_delete_task_success(self, client: TestClient):
        """Test deleting task by valid ID returns 204."""
        # Arrange
        with patch('app.api.tasks.delete_task', return_value=True):
            # Act
            response = client.delete(
                "/api/v1/tasks/task_123"
            )

        # Assert
        assert response.status_code == 204

    async def test_delete_task_not_found(self, client: TestClient):
        """Test deleting non-existent task returns 404."""
        # Arrange
        with patch('app.api.tasks.delete_task', return_value=False):
            # Act
            response = client.delete(
                "/api/v1/tasks/nonexistent_id"
            )

        # Assert
        assert response.status_code == 404


@pytest.fixture
def unauth_client():
    """Create a TestClient without authentication overrides for testing unauthorized access."""
    from app.api.dependencies import get_current_user, get_database

    # Clear all overrides
    app.dependency_overrides.clear()

    # Create fresh client without auth
    with TestClient(app=app) as client:
        yield client

    # Restore auth overrides for other tests
    from unittest.mock import MagicMock, AsyncMock

    async def restore_get_current_user():
        user = MagicMock()
        user.id = "test_user_123"
        user.email = "test@example.com"
        user.name = "Test User"
        return user

    async def restore_get_database():
        db = AsyncMock()
        db.tasks = AsyncMock()
        return db

    app.dependency_overrides[get_current_user] = restore_get_current_user
    app.dependency_overrides[get_database] = restore_get_database


class TestUnauthenticatedAccess:
    """Tests for unauthenticated access to task endpoints."""

    def test_unauthenticated_access_post(self, unauth_client: TestClient):
        """Test POST /tasks without authentication returns 403."""
        # Act
        response = unauth_client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "list_id": "list_456"
            }
        )

        # Assert - HTTPBearer returns 403 when no Authorization header provided
        assert response.status_code == 403

    def test_unauthenticated_access_get(self, unauth_client: TestClient):
        """Test GET /tasks/{id} without authentication returns 403."""
        # Act
        response = unauth_client.get("/api/v1/tasks/task_123")

        # Assert
        assert response.status_code == 403

    def test_unauthenticated_access_list(self, unauth_client: TestClient):
        """Test GET /tasks without authentication returns 403."""
        # Act
        response = unauth_client.get("/api/v1/tasks?list_id=list_456")

        # Assert
        assert response.status_code == 403

    def test_unauthenticated_access_put(self, unauth_client: TestClient):
        """Test PUT /tasks/{id} without authentication returns 403."""
        # Act
        response = unauth_client.put(
            "/api/v1/tasks/task_123",
            json={"title": "Updated Task"}
        )

        # Assert
        assert response.status_code == 403

    def test_unauthenticated_access_delete(self, unauth_client: TestClient):
        """Test DELETE /tasks/{id} without authentication returns 403."""
        # Act
        response = unauth_client.delete("/api/v1/tasks/task_123")

        # Assert
        assert response.status_code == 403
