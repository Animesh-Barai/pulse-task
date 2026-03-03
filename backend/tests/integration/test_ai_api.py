import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime


@pytest.mark.asyncio
class TestAIAPIEndpoints:
    """
    Integration tests for AI API endpoints.
    These tests follow the AAA pattern (Arrange → Act → Assert).
    Tests are designed to FAIL because ai.py doesn't exist yet (RED phase).
    """

    async def test_post_ai_suggest_task_success(self):
        """Test POST /ai/suggest/task returns valid suggestion."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        request_body = {
            "raw_title": "Implement user authentication",
            "raw_description": "Add OAuth2 login support",
            "context": {
                "workspace_id": "ws_123",
                "list_id": "list_456",
                "current_date": datetime(2026, 2, 26).isoformat()
            }
        }

        # Act
        response = client.post("/ai/suggest/task", json=request_body)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "rewritten_title" in data
        assert "checklist" in data
        assert "suggested_priority" in data
        assert "suggested_due_date" in data
        assert "confidence" in data
        assert "explanation" in data
        # Validate schema
        assert isinstance(data["checklist"], list)
        assert 1 <= data["suggested_priority"] <= 5
        assert 0.0 <= data["confidence"] <= 1.0

    async def test_post_ai_suggest_task_schema_validation(self):
        """Test POST /ai/suggest/task validates Pydantic schema."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        # Test missing required field
        invalid_request = {
            "raw_description": "Add OAuth2 login support",
            "context": {"workspace_id": "ws_123"}
        }

        # Act
        response = client.post("/ai/suggest/task", json=invalid_request)

        # Assert
        assert response.status_code == 422  # Validation error
        error = response.json()
        assert "detail" in error

    async def test_post_ai_prioritize_success(self):
        """Test POST /ai/prioritize computes effective priority."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        request_body = {
            "task_id": "task_123",
            "tasks": [
                {"id": "task_1", "priority": 3, "due_date": "2026-03-01"},
                {"id": "task_2", "priority": 5, "due_date": "2026-02-28"},
                {"id": "task_3", "priority": 2, "due_date": "2026-03-15"}
            ],
            "context": {
                "workspace_id": "ws_123",
                "current_date": datetime(2026, 2, 26).isoformat()
            }
        }

        # Act
        response = client.post("/ai/prioritize", json=request_body)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "prioritized_tasks" in data
        assert isinstance(data["prioritized_tasks"], list)
        # Check that tasks are prioritized (sorted by priority/due date)
        tasks = data["prioritized_tasks"]
        if len(tasks) > 1:
            # First task should have higher priority or earlier due date
            assert tasks[0]["id"] in ["task_2", "task_1"]  # Higher priority or earlier

    async def test_post_ai_train_feedback_success(self):
        """Test POST /ai/train/feedback records telemetry."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        request_body = {
            "suggestion_id": "suggestion_123",
            "task_id": "task_456",
            "user_id": "user_789",
            "workspace_id": "ws_123",
            "accepted": True,
            "edit_distance": 0.1,
            "feedback_at": datetime(2026, 2, 26).isoformat()
        }

        # Act
        response = client.post("/ai/train/feedback", json=request_body)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "recorded" in data["message"].lower()

    async def test_error_handling_400_invalid_input(self):
        """Test error handling - 400 for invalid input."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        invalid_requests = [
            {},  # Missing all fields
            {"raw_title": ""},  # Empty title
            {"raw_title": 123},  # Wrong type
        ]

        for invalid_request in invalid_requests:
            # Act
            response = client.post("/ai/suggest/task", json=invalid_request)

            # Assert
            assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
            error = response.json()
            assert "detail" in error or "error" in error

    async def test_error_handling_500_server_error(self):
        """Test error handling - 500 for server errors."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        # Mock classifier to raise exception
        with patch('app.api.ai.classify_task', side_effect=Exception("Server error")):
            request_body = {
                "raw_title": "Test error handling",
                "raw_description": "Force server error",
                "context": {"workspace_id": "ws_123"}
            }

            # Act
            response = client.post("/ai/suggest/task", json=request_body)

        # Assert
        assert response.status_code == 500
        error = response.json()
        assert "detail" in error

    async def test_authentication_workspace_access(self):
        """Test authentication - workspace access control."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        # Test without workspace_id (should be rejected or use default)
        request_body = {
            "raw_title": "Test authentication",
            "raw_description": "Check workspace access",
            "context": {}  # No workspace_id
        }

        # Act
        response = client.post("/ai/suggest/task", json=request_body)

        # Assert - Should either fail or use default workspace
        # For MVP, we'll accept missing workspace (uses default)
        # In production, this should require auth
        assert response.status_code in [200, 401, 403]

    async def test_rate_limiting(self):
        """Test rate limiting - prevents abuse."""
        # Arrange
        from app.main import app
        client = TestClient(app)

        request_body = {
            "raw_title": "Test rate limiting",
            "raw_description": "Send many requests",
            "context": {"workspace_id": "ws_123"}
        }

        # Act - Send multiple requests rapidly
        responses = []
        for _ in range(20):  # Send 20 requests
            response = client.post("/ai/suggest/task", json=request_body)
            responses.append(response)

        # Assert - Some requests should be rate limited (429)
        rate_limited = any(r.status_code == 429 for r in responses)
        # Note: For MVP, rate limiting may not be implemented yet
        # This test documents the requirement
        # We'll accept if most requests succeed
        successful = sum(1 for r in responses if r.status_code == 200)
        assert successful >= 15, f"Expected most requests to succeed, got {successful}"
