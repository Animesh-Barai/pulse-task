import pytest
from app.models.models import (
    UserCreate,
    User,
    WorkspaceCreate,
    Workspace,
    ListCreate,
    TaskList,
    TaskCreate,
    TaskUpdate,
    Task,
    AISuggestion,
    AISuggestionRequest,
    AISuggestionResponse,
    TaskStatus,
    Priority,
    UserRole
)
from datetime import datetime
from pydantic import ValidationError


class TestUserModels:
    def test_user_create_valid(self):
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "securepassword123"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.password == "securepassword123"

    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(email="invalid-email", name="Test", password="password123")

    def test_user_create_short_password(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", name="Test", password="short")

    def test_user_model_serialization(self):
        user = User(
            id="123",
            email="test@example.com",
            name="Test User",
            created_at=datetime.utcnow()
        )
        assert user.id == "123"
        assert user.email == "test@example.com"
        assert isinstance(user.created_at, datetime)


class TestWorkspaceModels:
    def test_workspace_create_valid(self):
        workspace = WorkspaceCreate(name="Test Workspace")
        assert workspace.name == "Test Workspace"

    def test_workspace_model_valid(self):
        workspace = Workspace(
            id="123",
            name="Test Workspace",
            owner_id="user_123",
            member_ids=["user_123", "user_456"],
            region="us-east-1"
        )
        assert workspace.id == "123"
        assert workspace.owner_id == "user_123"
        assert len(workspace.member_ids) == 2


class TestListModels:
    def test_list_create_valid(self):
        task_list = ListCreate(title="My Tasks", workspace_id="workspace_123")
        assert task_list.title == "My Tasks"
        assert task_list.workspace_id == "workspace_123"

    def test_task_list_model_valid(self):
        task_list = TaskList(
            id="123",
            title="My Tasks",
            workspace_id="workspace_123",
            y_doc_key="ydoc_key_123"
        )
        assert task_list.y_doc_key == "ydoc_key_123"


class TestTaskModels:
    def test_task_create_valid(self):
        task = TaskCreate(
            title="Test Task",
            list_id="list_123",
            assignee_id="user_123",
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS
        )
        assert task.title == "Test Task"
        assert task.list_id == "list_123"
        assert task.assignee_id == "user_123"
        assert task.priority == Priority.HIGH
        assert task.status == TaskStatus.IN_PROGRESS

    def test_task_update_partial(self):
        task_update = TaskUpdate(title="Updated Title")
        assert task_update.title == "Updated Title"
        assert task_update.description is None

    def test_task_model_valid(self):
        task = Task(
            id="123",
            title="Test Task",
            list_id="list_123",
            status=TaskStatus.OPEN,
            priority=Priority.MEDIUM
        )
        assert task.id == "123"
        assert task.status == TaskStatus.OPEN

    def test_task_status_enum(self):
        assert TaskStatus.OPEN == "OPEN"
        assert TaskStatus.IN_PROGRESS == "IN_PROGRESS"
        assert TaskStatus.DONE == "DONE"

    def test_priority_enum(self):
        assert Priority.LOW == 1
        assert Priority.MEDIUM == 2
        assert Priority.HIGH == 3
        assert Priority.CRITICAL == 4
        assert Priority.URGENT == 5


class TestAIModels:
    def test_ai_suggestion_request(self):
        request = AISuggestionRequest(
            raw_title="Fix landing page",
            raw_description="The landing page has issues",
            context={"workspace_type": "marketing"}
        )
        assert request.raw_title == "Fix landing page"
        assert request.context is not None

    def test_ai_suggestion_response(self):
        response = AISuggestionResponse(
            id="123",
            task_id="task_123",
            workspace_id="workspace_123",
            rewritten_title="Improve landing page conversion rate",
            checklist=["Analyze funnel", "Design variants"],
            priority=3,
            due_date=datetime(2026, 2, 1),
            explanation="Marketing conversion intent detected",
            confidence=0.86,
            accepted=False
        )
        assert response.rewritten_title == "Improve landing page conversion rate"
        assert len(response.checklist) == 2
        assert response.confidence == 0.86

    def test_ai_suggestion_with_null_values(self):
        suggestion = AISuggestion(
            task_id="task_123",
            workspace_id="workspace_123",
            rewritten_title=None,
            checklist=[],
            priority=None,
            due_date=None,
            explanation="Insufficient context",
            confidence=0.23
        )
        assert suggestion.rewritten_title is None
        assert len(suggestion.checklist) == 0
        assert suggestion.confidence < 0.5


class TestUserRole:
    def test_user_role_enum(self):
        assert UserRole.OWNER == "owner"
        assert UserRole.ADMIN == "admin"
        assert UserRole.MEMBER == "member"
        assert UserRole.GUEST == "guest"
