"""
Unit Tests for Presence Service and Socket.IO Events

Tests Redis-based presence tracking and Socket.IO event handlers.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.presence_service import (
    update_user_presence,
    set_user_typing,
    update_cursor_position,
    get_workspace_users,
    get_user_typing_status,
    get_cursor_positions,
    remove_user_presence,
    cleanup_expired_presence
)


@pytest.mark.asyncio
async def test_update_user_presence_success():
    """Test successful user presence update."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)

    result = await update_user_presence(
        user_id="user_123",
        workspace_id="ws_123",
        presence="online",
        user_name="John Doe",
        redis_client=mock_redis
    )

    assert result is True
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_presence_without_redis():
    """Test presence update without Redis client."""
    result = await update_user_presence(
        user_id="user_123",
        workspace_id="ws_123",
        presence="online",
        redis_client=None
    )

    assert result is False


@pytest.mark.asyncio
async def test_set_user_typing_true():
    """Test setting typing indicator to true."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)

    result = await set_user_typing(
        user_id="user_123",
        workspace_id="ws_123",
        is_typing=True,
        redis_client=mock_redis
    )

    assert result is True
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_set_user_typing_false():
    """Test clearing typing indicator."""
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock(return_value=True)

    result = await set_user_typing(
        user_id="user_123",
        workspace_id="ws_123",
        is_typing=False,
        redis_client=mock_redis
    )

    assert result is True
    mock_redis.delete.assert_called_once()


@pytest.mark.asyncio
async def test_update_cursor_position():
    """Test updating cursor position."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)

    result = await update_cursor_position(
        user_id="user_123",
        workspace_id="ws_123",
        list_id="list_456",
        task_id="task_789",
        position={"line": 5, "column": 10},
        redis_client=mock_redis
    )

    assert result is True
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_get_workspace_users():
    """Test getting all users in workspace."""
    mock_redis = AsyncMock()
    
    # Mock the keys method to return our test keys
    async def mock_keys_func(pattern):
        if pattern == "presence:ws_123:*":
            return [b"presence:ws_123:user_1", b"presence:ws_123:user_2"]
        return []
    
    mock_redis.keys = mock_keys_func
    
    # Mock the get method to return user data
    # Create a custom function that handles specific keys
    def get_data(key):
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        
        if key == "presence:ws_123:user_1":
            return bytes(json.dumps({"user_id": "user_1", "presence": "online"}), 'utf-8')
        elif key == "presence:ws_123:user_2":
            return bytes(json.dumps({"user_id": "user_2", "presence": "offline"}), 'utf-8')
        elif key == "cursor:ws_123:user_1":
            return bytes(json.dumps({"position": {"line": "5", "column": "10"}}), 'utf-8')
        elif key == "cursor:ws_123:user_2":
            return bytes(json.dumps({"position": {"line": "8", "column": "8"}}), 'utf-8')
        return None
    
    mock_redis.get = AsyncMock(side_effect=get_data)

    users = await get_workspace_users(
        workspace_id="ws_123",
        redis_client=mock_redis
    )

    assert len(users) == 2
    assert users[0]["user_id"] == "user_1"
    assert users[1]["presence"] == "offline"
    cursor = users[0].get("cursor", {})
    assert cursor is not None, "Cursor should not be None"
    line_value = cursor.get("position", {}).get("line")
    assert isinstance(line_value, (int, str)), f"Line value is {type(line_value)}: {line_value}"
    assert int(line_value) == 5, f"Expected line 5, got {line_value}"


@pytest.mark.asyncio
async def test_get_workspace_users_empty():
    """Test getting users when workspace is empty."""
    mock_redis = AsyncMock()
    mock_redis.keys = AsyncMock(return_value=[])

    users = await get_workspace_users(
        workspace_id="ws_empty",
        redis_client=mock_redis
    )

    assert len(users) == 0


@pytest.mark.asyncio
async def test_get_user_typing_status():
    """Test getting typing status for multiple users."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=[
        b'{"is_typing": true}',
        None
    ])

    typing_status = await get_user_typing_status(
        workspace_id="ws_123",
        user_ids=["user_1", "user_2"],
        redis_client=mock_redis
    )

    assert typing_status["user_1"] is True
    assert typing_status["user_2"] is False


@pytest.mark.asyncio
async def test_get_cursor_positions():
    """Test getting cursor positions for multiple users."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=[
        b'{"position": {"line": 5, "column": 10}}',
        b'{"position": {"line": 8, "column": 8}}'
    ])

    cursor_positions = await get_cursor_positions(
        workspace_id="ws_123",
        user_ids=["user_1", "user_2"],
        redis_client=mock_redis
    )

    assert cursor_positions["user_1"]["position"]["line"] == 5
    assert cursor_positions["user_2"]["position"]["line"] == 8


@pytest.mark.asyncio
async def test_remove_user_presence():
    """Test removing user presence."""
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock(return_value=True)

    result = await remove_user_presence(
        user_id="user_123",
        workspace_id="ws_123",
        redis_client=mock_redis
    )

    assert result is True
    # Should delete 3 keys (presence, cursor, typing)
    assert mock_redis.delete.call_count == 3


@pytest.mark.asyncio
async def test_cleanup_expired_presence():
    """Test cleaning up expired presence."""
    mock_redis = AsyncMock()
    mock_redis.keys = AsyncMock(side_effect=[
        [b"presence:ws_123:user_1"],
        [b"cursor:ws_123:user_1"],
        [b"typing:ws_123:user_1"]
    ])

    mock_redis.ttl = AsyncMock(return_value=-1)  # Expired
    mock_redis.delete = AsyncMock(return_value=True)

    cleaned_count = await cleanup_expired_presence(
        workspace_id="ws_123",
        redis_client=mock_redis
    )

    assert cleaned_count == 3
    assert mock_redis.delete.call_count == 3
