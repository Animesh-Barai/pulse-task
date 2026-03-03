import pytest
from datetime import datetime
from unittest.mock import MagicMock
from typing import Dict, Any


@pytest.mark.asyncio
class TestHeuristicsService:
    """
    Unit tests for the heuristics service.
    These tests follow the AAA pattern (Arrange → Act → Assert).
    Tests are designed to FAIL because heuristics_service doesn't exist yet (RED phase).
    """

    async def test_date_extraction_by_friday(self):
        """Test extracting date from 'by Friday' pattern."""
        # Arrange
        raw_title = "Complete documentation by Friday"
        raw_description = "Write API documentation"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 25)  # Wednesday
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "suggested_due_date" in result
        assert result["suggested_due_date"] == "2026-02-27"  # Friday (Wednesday + 2 days)

    async def test_date_extraction_asap(self):
        """Test extracting date from 'ASAP' pattern."""
        # Arrange
        raw_title = "Fix critical bug ASAP"
        raw_description = "Authentication failure on login"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "suggested_due_date" in result
        # ASAP should suggest due date within 24 hours (next day)
        assert result["suggested_due_date"] == "2026-02-27"

    async def test_date_extraction_urgent(self):
        """Test extracting date from 'urgent' pattern."""
        # Arrange
        raw_title = "Urgent: Deploy hotfix"
        raw_description = "Critical security vulnerability"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "suggested_due_date" in result
        # Urgent should suggest due date within 48 hours
        assert result["suggested_due_date"] in ["2026-02-27", "2026-02-28"]

    async def test_priority_detection_keywords(self):
        """Test priority detection from keywords (urgent, asap, critical)."""
        # Arrange
        test_cases = [
            ("urgent fix", 5),      # Urgent -> priority 5 (highest)
            ("ASAP task", 5),       # ASAP -> priority 5
            ("critical bug", 5),    # Critical -> priority 5
            ("high priority", 4),   # High -> priority 4
            ("medium task", 3),     # Medium -> priority 3
            ("low priority", 2),    # Low -> priority 2
            ("nice to have", 1),    # Nice to have -> priority 1 (lowest)
        ]

        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        for raw_title, expected_priority in test_cases:
            # Act
            from app.services.heuristics_service import generate_suggestion
            result = await generate_suggestion(raw_title, "", context)

            # Assert
            assert result["suggested_priority"] == expected_priority

    async def test_checklist_generation_simple_task(self):
        """Test generating checklist for simple task."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add login and registration"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "checklist" in result
        assert isinstance(result["checklist"], list)
        assert len(result["checklist"]) >= 1  # At least one checklist item
        # Checklist items should be strings
        assert all(isinstance(item, str) for item in result["checklist"])

    async def test_title_rewriting_action_verbs(self):
        """Test title rewriting to ensure action verbs."""
        # Arrange
        raw_title = "user authentication"  # Missing action verb
        raw_description = "Add login and registration"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "rewritten_title" in result
        assert len(result["rewritten_title"]) > 0
        # Rewritten title should start with an action verb (improve, implement, add, etc.)
        action_verbs = ["implement", "create", "add", "fix", "update", "improve", "deploy", "refactor", "test"]
        rewritten_lower = result["rewritten_title"].lower()
        assert any(verb in rewritten_lower for verb in action_verbs)

    async def test_edge_cases_empty_input(self):
        """Test handling empty input."""
        # Arrange
        raw_title = ""
        raw_description = ""
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act & Assert
        from app.services.heuristics_service import generate_suggestion
        with pytest.raises(ValueError) as exc_info:
            await generate_suggestion(raw_title, raw_description, context)

        assert "empty" in str(exc_info.value).lower()

    async def test_edge_cases_malformed_dates(self):
        """Test handling malformed date patterns."""
        # Arrange
        raw_title = "Complete task by notarealdate"
        raw_description = "This has an invalid date pattern"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "suggested_due_date" in result
        # Malformed date should result in None, not a crash
        assert result["suggested_due_date"] is None

    async def test_confidence_scoring(self):
        """Test confidence scoring based on input clarity."""
        # Arrange
        test_cases = [
            ("Implement user login", 0.9),  # Clear, specific
            ("fix bug", 0.6),               # Vague but actionable
            ("do stuff", 0.2),              # Very vague
        ]

        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        for raw_title, min_expected_confidence in test_cases:
            # Act
            from app.services.heuristics_service import generate_suggestion
            result = await generate_suggestion(raw_title, "", context)

            # Assert
            assert result is not None
            assert "confidence" in result
            assert 0.0 <= result["confidence"] <= 1.0
            assert result["confidence"] >= min_expected_confidence

    async def test_validation_invalid_inputs(self):
        """Test validation of invalid inputs."""
        # Arrange
        # None input
        raw_title = None
        raw_description = "Valid description"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act & Assert
        from app.services.heuristics_service import generate_suggestion
        with pytest.raises(ValueError):
            await generate_suggestion(raw_title, raw_description, context)

    async def test_integration_with_task_context(self):
        """Test integration with task context (workspace, tags, etc.)."""
        # Arrange
        raw_title = "Deploy to production"
        raw_description = "Deploy latest version to prod environment"
        context = {
            "workspace_id": "ws_123",
            "list_id": "list_456",
            "tags": ["deployment", "production"],
            "assignee_id": "user_789",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "rewritten_title" in result
        assert "checklist" in result
        assert "suggested_priority" in result
        assert "suggested_due_date" in result
        assert "confidence" in result
        assert "explanation" in result
        # Result should be a complete suggestion
        assert isinstance(result["rewritten_title"], str)
        assert isinstance(result["checklist"], list)
        assert isinstance(result["suggested_priority"], int)
        assert 1 <= result["suggested_priority"] <= 5
        assert isinstance(result["confidence"], float)
        assert isinstance(result["explanation"], str)

    async def test_explanation_generation(self):
        """Test explanation generation for suggestions."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add OAuth2 login support"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.heuristics_service import generate_suggestion
        result = await generate_suggestion(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "explanation" in result
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0
        # Explanation should be a short, readable string
        assert len(result["explanation"]) < 300
