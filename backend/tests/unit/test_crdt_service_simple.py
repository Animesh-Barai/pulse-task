import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List
from app.models.models import TaskList
from app.services.crdt_service import create_ydoc, get_ydoc, update_ydoc_snapshot, delete_ydoc, list_ydocs_by_workspace
from app.services.presence_service import update_user_presence, get_workspace_users, remove_user_presence
from app.services.offline_service import queue_offline_operations, get_queued_operations, clear_queued_operations
from app.services.socket_helpers import user_join_workspace, user_leave_workspace, broadcast_to_workspace


@pytest.mark.asyncio
class TestCRDTServiceSimple:
    async def test_create_ydoc_success(self):
        """Test creating a new Yjs document (list)."""
        mock_db = AsyncMock()
        mock_result = MagicMock(inserted_id="ydoc_123")

        mock_db.ydocs = MagicMock()
        mock_insert = AsyncMock(return_value=mock_result)
        mock_db.ydocs.insert_one = mock_insert

        result = await create_ydoc("workspace_123", "My Task List", mock_db)

        assert result is not None
        assert result.id == "ydoc_123"
        assert result.title == "My Task List"
        assert result.workspace_id == "workspace_123"

    async def test_get_ydoc_exists(self):
        """Test getting an existing Yjs document."""
        mock_db = AsyncMock()
        mock_doc = {
            "_id": "ydoc_123",
            "workspace_id": "workspace_123",
            "title": "My Task List",
            "y_doc_key": "doc_key_abc",
            "created_at": "2024-01-01T00:00:00"
        }

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.find_one = AsyncMock(return_value=mock_doc)

        result = await get_ydoc("ydoc_abc", mock_db)

        assert result is not None
        assert result.title == "My Task List"

    async def test_update_ydoc_snapshot_success(self):
        """Test updating Yjs document snapshot."""
        mock_db = AsyncMock()
        mock_update = AsyncMock()
        mock_update.return_value = MagicMock(modified_count=1)

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.update_one = mock_update

        result = await update_ydoc_snapshot(
            "ydoc_abc",
            {"yjs_state": b"binary_data"},
            {"version": 123, "size": 1024},
            mock_db
        )

        assert result is True
        mock_update.assert_called_once()

    async def test_delete_ydoc_success(self):
        """Test deleting a Yjs document."""
        mock_db = AsyncMock()
        mock_delete = AsyncMock()
        mock_delete.return_value = MagicMock(deleted_count=1)

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.delete_one = mock_delete

        result = await delete_ydoc("ydoc_abc", mock_db)

        assert result is True
        mock_delete.assert_called_once()

    async def test_list_ydocs_by_workspace(self):
        """Test listing Yjs documents by workspace."""
        mock_db = AsyncMock()
        mock_cursor = MagicMock()
        mock_result = [
            {"id": "ydoc_1", "workspace_id": "workspace_123", "title": "List 1", "y_doc_key": "key_1"},
            {"id": "ydoc_2", "workspace_id": "workspace_123", "title": "List 2", "y_doc_key": "key_2"}
        ]

        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_result)

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.find = MagicMock(return_value=mock_cursor)

        result = await list_ydocs_by_workspace("workspace_123", mock_db)

        assert result is not None
        assert len(result) == 2
        assert result[0].title == "List 1"
        assert result[1].title == "List 2"


@pytest.mark.asyncio
class TestPresenceServiceSimple:
    async def test_track_user_presence(self):
        """Test tracking user presence in workspace."""
        mock_redis = AsyncMock()

        mock_set = AsyncMock()
        mock_redis.setex = mock_set

        await update_user_presence(
            "user_123",
            "workspace_123",
            "online",
            mock_redis
        )

        mock_set.assert_called_once()

    async def test_get_workspace_users(self):
        """Test getting all online users in workspace."""
        mock_redis = AsyncMock()

        async def mock_get(key):
            if "user_123" in key:
                return b'{"user_id": "user_123", "presence": "online"}'
            elif "user_456" in key:
                return b'{"user_id": "user_456", "presence": "online"}'
            return None

        mock_redis.keys = AsyncMock(return_value=[f"presence:workspace_123:user_123", f"presence:workspace_123:user_456"])
        mock_redis.get = mock_get

        result = await get_workspace_users("workspace_123", mock_redis)

        assert result is not None
        assert len(result) == 2
        assert result[0]["user_id"] == "user_123"
        assert result[1]["presence"] == "online"
        assert result[0]["presence"] == "online"

    async def test_remove_user_presence(self):
        """Test removing user presence from workspace."""
        mock_redis = AsyncMock()
        mock_delete = AsyncMock()

        mock_redis.delete = mock_delete

        result = await remove_user_presence("user_123", "workspace_123", mock_redis)

        assert result is True
        mock_delete.assert_called_once()


@pytest.mark.asyncio
class TestOfflineMergeServiceSimple:
    async def test_queue_offline_operations(self):
        """Test queuing offline operations for later sync."""
        mock_redis = AsyncMock()
        mock_lpush = AsyncMock()
        mock_redis.lpush = mock_lpush

        await queue_offline_operations(
            "user_123",
            "ydoc_abc",
            [{"type": "insert", "text": "Task 1"}],
            mock_redis
        )

        mock_lpush.assert_called_once()

    async def test_get_queued_operations(self):
        """Test getting queued operations for syncing."""
        mock_redis = AsyncMock()
        mock_lrange = AsyncMock()
        mock_lrange.return_value = [
            b'{"type": "insert", "text": "Task 1"}',
            b'{"type": "insert", "text": "Task 2"}'
        ]

        mock_redis.lrange = mock_lrange

        result = await get_queued_operations("user_123", "ydoc_abc", mock_redis)

        assert result is not None
        assert len(result) == 2
        assert result[0]["type"] == "insert"
        assert result[0]["text"] == "Task 1"
        assert result[1]["type"] == "insert"

    async def test_clear_queued_operations(self):
        """Test clearing queued operations after sync."""
        mock_redis = AsyncMock()
        mock_delete = AsyncMock()
        mock_delete.return_value = 1

        mock_redis.delete = mock_delete

        result = await clear_queued_operations("user_123", "ydoc_abc", mock_redis)

        assert result is True
        mock_delete.assert_called_once()


@pytest.mark.asyncio
class TestSocketEventsSimple:
    async def test_user_join_workspace(self):
        """Test user joining workspace room."""
        mock_socket_manager = MagicMock()

        user_join_workspace("user_123", "Alice", "workspace_123")

        # Just verify it doesn't crash (the simple_socket_manager is a real object)
        assert True

    async def test_user_leave_workspace(self):
        """Test user leaving workspace room."""
        user_leave_workspace("user_123", "workspace_123")

        # Just verify it doesn't crash
        assert True

    async def test_broadcast_to_workspace(self):
        """Test broadcasting events to workspace members."""
        broadcast_to_workspace("test_event", {"data": "test"}, "workspace_123")

        # Just verify it doesn't crash
        assert True
