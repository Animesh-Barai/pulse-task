import pytest
from datetime import datetime
from typing import Dict, Any


@pytest.mark.asyncio
class TestClassifierService:
    """
    Unit tests for the local classifier service.
    These tests follow the AAA pattern (Arrange → Act → Assert).
    Tests are designed to FAIL because classifier_service doesn't exist yet (RED phase).
    """

    @pytest.fixture(autouse=True)
    def mock_ai_service(self, monkeypatch):
        """Mock the outbound HTTP calls to the AI service by patching mock_classify."""
        from app.services.classifier_service import heuristics_suggest
        async def mock_classify_func(raw_title, raw_description, context):
            return await heuristics_suggest(raw_title, raw_description, context)
        monkeypatch.setattr("app.services.classifier_service.mock_classify", mock_classify_func)

    async def test_mock_classifier_input_output(self):
        """Test mock classifier with known input/output."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add OAuth2 login support"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.classifier_service import classify_task
        result = await classify_task(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "rewritten_title" in result
        assert "checklist" in result
        assert "suggested_priority" in result
        assert "suggested_due_date" in result
        assert "confidence" in result
        assert "explanation" in result
        # Verify schema types
        assert isinstance(result["rewritten_title"], str)
        assert isinstance(result["checklist"], list)
        assert isinstance(result["suggested_priority"], int)
        assert 1 <= result["suggested_priority"] <= 5
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["explanation"], str)

    async def test_confidence_threshold_high(self):
        """Test high confidence threshold (>= 0.8)."""
        # Arrange
        raw_title = "Implement user authentication with OAuth2"  # Clear, specific
        raw_description = "Add login and registration with Google and GitHub"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.classifier_service import classify_task
        result = await classify_task(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "confidence" in result
        assert result["confidence"] >= 0.8  # High confidence

    async def test_confidence_threshold_review(self):
        """Test review confidence threshold (0.5 - 0.8)."""
        # Arrange
        raw_title = "Update code"  # Somewhat vague
        raw_description = "Add new functionality"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.classifier_service import classify_task
        result = await classify_task(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "confidence" in result
        assert 0.5 <= result["confidence"] < 0.8  # Review range

    async def test_confidence_threshold_low(self):
        """Test low confidence threshold (< 0.5)."""
        # Arrange
        raw_title = "do stuff"  # Very vague
        raw_description = "Fix things"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.classifier_service import classify_task
        result = await classify_task(raw_title, raw_description, context)

        # Assert
        assert result is not None
        assert "confidence" in result
        assert result["confidence"] < 0.5  # Low confidence

    async def test_schema_validation(self):
        """Test schema validation (JSON structure)."""
        # Arrange
        raw_title = "Test schema validation"
        raw_description = "Ensure output matches required schema"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.classifier_service import classify_task
        result = await classify_task(raw_title, raw_description, context)

        # Assert - Verify all required fields are present
        required_fields = [
            "rewritten_title",
            "checklist",
            "suggested_priority",
            "suggested_due_date",
            "confidence",
            "explanation"
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Verify field types
        assert isinstance(result["rewritten_title"], str), "rewritten_title must be string"
        assert isinstance(result["checklist"], list), "checklist must be list"
        assert isinstance(result["suggested_priority"], int), "suggested_priority must be int"
        assert isinstance(result["confidence"], float), "confidence must be float"
        assert isinstance(result["explanation"], str), "explanation must be string"
        assert result["suggested_due_date"] is None or isinstance(result["suggested_due_date"], str), "suggested_due_date must be string or null"

        # Verify value ranges
        assert 1 <= result["suggested_priority"] <= 5, "suggested_priority must be 1-5"
        assert 0.0 <= result["confidence"] <= 1.0, "confidence must be 0.0-1.0"
        if result["suggested_due_date"]:
            # Validate ISO date format (YYYY-MM-DD)
            assert len(result["suggested_due_date"]) == 10, "suggested_due_date must be YYYY-MM-DD format"
            datetime.strptime(result["suggested_due_date"], "%Y-%m-%d")

    async def test_latency_requirement(self):
        """Test latency requirement (< 50ms)."""
        # Arrange
        raw_title = "Test latency"
        raw_description = "Ensure classification is fast"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.classifier_service import classify_task
        import time
        start_time = time.perf_counter()
        result = await classify_task(raw_title, raw_description, context)
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # Assert
        assert result is not None
        assert latency_ms < 50, f"Latency {latency_ms:.2f}ms exceeds 50ms requirement"

    async def test_fallback_to_heuristics(self):
        """Test fallback to heuristics on classifier failure."""
        # Arrange
        raw_title = "Test fallback"
        raw_description = "Classifier should fallback on error"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26),
            "force_fallback": True  # Force fallback for testing
        }

        # Act
        from app.services.classifier_service import classify_task
        result = await classify_task(raw_title, raw_description, context)

        # Assert - Should still return a valid suggestion using heuristics
        assert result is not None
        assert "rewritten_title" in result
        assert "checklist" in result
        assert "suggested_priority" in result
        assert "suggested_due_date" in result
        assert "confidence" in result
        assert "explanation" in result

    async def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Arrange
        raw_title = None  # Invalid input
        raw_description = "Valid description"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act & Assert
        from app.services.classifier_service import classify_task
        with pytest.raises(ValueError) as exc_info:
            await classify_task(raw_title, raw_description, context)

        assert "title" in str(exc_info.value).lower()
