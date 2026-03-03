import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime


@pytest.mark.asyncio
class TestCacheService:
    """
    Unit tests for the cache service.
    These tests follow the AAA pattern (Arrange → Act → Assert).
    Tests are designed to FAIL because cache_service doesn't exist yet (RED phase).
    """

    async def test_cache_hit_scenario(self):
        """Test cache hit - retrieve cached suggestion."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add OAuth2 login"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Cached result to simulate cache hit
        cached_result = {
            "rewritten_title": "Implement user authentication with OAuth2",
            "checklist": ["Design auth flow", "Implement login", "Implement registration"],
            "suggested_priority": 5,
            "suggested_due_date": "2026-03-01",
            "confidence": 0.9,
            "explanation": "High confidence - clear task with specific technology"
        }

        # Need to serialize to JSON for realistic mock behavior
        import json
        mock_redis = MagicMock()
        mock_redis.get = MagicMock(return_value=json.dumps(cached_result))

        # Act
        from app.services.cache_service import get_cached_suggestion
        result = get_cached_suggestion(raw_title, raw_description, context, mock_redis)

        # Assert
        assert result is not None
        assert result == cached_result
        mock_redis.get.assert_called_once()

    async def test_cache_miss_scenario(self):
        """Test cache miss - return None when no cached value exists."""
        # Arrange
        raw_title = "New task title"
        raw_description = "Description"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        mock_redis = MagicMock()
        mock_redis.get = MagicMock(return_value=None)
        mock_redis.get.return_value = None  # Ensure it returns None, not a coroutine

        # Act
        from app.services.cache_service import get_cached_suggestion
        result = get_cached_suggestion(raw_title, raw_description, context, mock_redis)

        # Assert
        assert result is None
        mock_redis.get.assert_called_once()

    async def test_cache_key_generation(self):
        """Test cache key generation using hash of input."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add OAuth2 login"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        # Act
        from app.services.cache_service import generate_cache_key
        cache_key = generate_cache_key(raw_title, raw_description, context)

        # Assert
        assert cache_key is not None
        assert isinstance(cache_key, str)
        # Cache key should be a hash + prefix (consistent for same inputs)
        # Prefix "ai:suggestion:" (14 chars) + SHA-256 hash (64 chars) = 78 chars
        assert len(cache_key) == 78
        # Same inputs should produce same key
        cache_key2 = generate_cache_key(raw_title, raw_description, context)
        assert cache_key == cache_key2
        # Different inputs should produce different keys
        cache_key3 = generate_cache_key("Different task", "Different description", context)
        assert cache_key != cache_key3
        # Cache key should start with prefix
        assert cache_key.startswith("ai:suggestion:")

    async def test_cache_expiration_ttl(self):
        """Test cache expiration with TTL (Time To Live)."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add OAuth2 login"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        suggestion = {
            "rewritten_title": "Implement user authentication with OAuth2",
            "checklist": ["Design", "Implement", "Test"],
            "suggested_priority": 5,
            "suggested_due_date": "2026-03-01",
            "confidence": 0.9,
            "explanation": "High confidence"
        }

        mock_redis = MagicMock()
        mock_redis.setex = MagicMock()

        # Act
        from app.services.cache_service import cache_suggestion
        cache_suggestion(raw_title, raw_description, context, suggestion, mock_redis)

        # Assert
        assert mock_redis.setex.called
        # Check that TTL was set (should be 24 hours = 86400 seconds)
        call_args = mock_redis.setex.call_args
        cache_key = call_args[0][0]
        ttl = call_args[0][1]
        assert isinstance(ttl, int)
        assert ttl > 0  # TTL should be positive
        # TTL should be approximately 24 hours (86400 seconds)
        assert 80000 <= ttl <= 90000  # Allow some flexibility

    async def test_cache_invalidation_feedback(self):
        """Test cache invalidation on feedback updates."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add OAuth2 login"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        mock_redis = MagicMock()
        mock_redis.delete = MagicMock()

        # Act
        from app.services.cache_service import invalidate_cache
        invalidate_cache(raw_title, raw_description, context, mock_redis)

        # Assert
        mock_redis.delete.assert_called_once()
        # Verify correct cache key was deleted
        call_args = mock_redis.delete.call_args
        assert call_args[0][0] is not None
        assert isinstance(call_args[0][0], str)

    async def test_performance_cache_lookup(self):
        """Test performance requirement - cache lookup <5ms."""
        # Arrange
        raw_title = "Implement user authentication"
        raw_description = "Add OAuth2 login"
        context = {
            "workspace_id": "ws_123",
            "current_date": datetime(2026, 2, 26)
        }

        cached_result = {
            "rewritten_title": "Implement user authentication",
            "checklist": ["Design", "Implement", "Test"],
            "suggested_priority": 5,
            "suggested_due_date": "2026-03-01",
            "confidence": 0.9,
            "explanation": "High confidence"
        }

        import json
        mock_redis = MagicMock()
        mock_redis.get = MagicMock(return_value=json.dumps(cached_result))

        # Act
        import time
        from app.services.cache_service import get_cached_suggestion
        start_time = time.perf_counter()
        result = get_cached_suggestion(raw_title, raw_description, context, mock_redis)
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # Assert
        assert result is not None
        assert latency_ms < 5, f"Cache lookup took {latency_ms:.2f}ms, exceeding 5ms requirement"
