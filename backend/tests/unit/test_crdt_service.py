import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json
from app.models.models import TaskList
from app.services.crdt_service import create_ydoc, get_ydoc
from app.services.presence_service import update_user_presence, remove_user_presence
from app.services.offline_service import queue_offline_operations
from app.services.socket_helpers import (
    handle_ydoc_update,
    simple_socket_manager,
    user_join_workspace,
    user_leave_workspace,
    broadcast_to_workspace
)


@pytest.mark.asyncio
class TestCRDTService:
    async def test_create_ydoc_success(self):
        """Test creating a new Yjs document (list)."""
        mock_db = AsyncMock()
        mock_result = MagicMock(inserted_id="ydoc_123")
        mock_result.title = "My Task List"

        mock_insert = AsyncMock(return_value=mock_result)
        mock_db.ydocs = MagicMock()
        mock_db.ydocs.insert_one = mock_insert

        from app.services.crdt_service import create_ydoc

        result = await create_ydoc("list_123", "My Task List", mock_db)

        assert result is not None
        assert result.id == "ydoc_123"
        assert result.title == "My Task List"

    async def test_get_ydoc_exists(self):
        """Test getting an existing Yjs document."""
        mock_db = AsyncMock()
        mock_doc = {
            "_id": "ydoc_123",
            "workspace_id": "list_123",
            "title": "My Task List",
            "y_doc_key": "doc_key_abc",
            "created_at": datetime.utcnow()
        }

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.find_one = AsyncMock(return_value=mock_doc)

        from app.services.crdt_service import get_ydoc
        result = await get_ydoc("doc_key_abc", mock_db)

        assert result is not None
        assert result.title == "My Task List"

    async def test_get_ydoc_not_exists(self):
        """Test getting a non-existent Yjs document."""
        mock_db = AsyncMock()
        mock_db.ydocs = MagicMock()
        mock_db.ydocs.find_one = AsyncMock(return_value=None)

        from app.services.crdt_service import get_ydoc
        result = await get_ydoc("nonexistent", mock_db)

        assert result is None

    async def test_update_ydoc_snapshot_success(self):
        """Test updating Yjs document snapshot."""
        mock_db = AsyncMock()
        mock_update = AsyncMock()
        mock_update.return_value = MagicMock(modified_count=1)

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.update_one = mock_update

        from app.services.crdt_service import update_ydoc_snapshot

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

        from app.services.crdt_service import delete_ydoc

        result = await delete_ydoc("ydoc_abc", mock_db)

        assert result is True
        mock_delete.assert_called_once()

    async def test_list_ydocs_by_workspace(self):
        """Test listing Yjs documents by workspace."""
        mock_db = AsyncMock()
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": "ydoc_1", "title": "List 1", "workspace_id": "list_123", "y_doc_key": "key1", "created_at": datetime.utcnow()},
            {"_id": "ydoc_2", "title": "List 2", "workspace_id": "list_123", "y_doc_key": "key2", "created_at": datetime.utcnow()}
        ])

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.find = MagicMock(return_value=mock_cursor)

        from app.services.crdt_service import list_ydocs_by_workspace

        result = await list_ydocs_by_workspace("workspace_123", mock_db)

        assert result is not None
        assert len(result) == 2
        assert result[0].title == "List 1"
        assert result[1].title == "List 2"


@pytest.mark.asyncio
class TestPresenceService:
    async def test_track_user_presence(self):
        """Test tracking user presence in workspace."""
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()

        fixed_dt = datetime(2026, 2, 26, 12, 0, 0)
        with patch('app.services.presence_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = fixed_dt

            await update_user_presence(
                user_id="user_123",
                workspace_id="workspace_123",
                presence="online",
                user_name="Alice",
                redis_client=mock_redis
            )

        mock_redis.setex.assert_called_once()
        args, kwargs = mock_redis.setex.call_args
        assert args[0] == "presence:workspace_123:user_123"
        assert args[1] == 300
        val = json.loads(args[2])
        assert val["user_id"] == "user_123"
        assert val["presence"] == "online"
        assert val["last_seen"] == fixed_dt.isoformat()

    async def test_get_workspace_users(self):
        """Test getting all online users in workspace."""
        mock_redis = AsyncMock()
        mock_redis.keys = AsyncMock(return_value=[
            "presence:workspace_123:user_123",
            "presence:workspace_123:user_456"
        ])
        
        async def mock_get(key):
            if "user_123" in key:
                return json.dumps({"user_id": "user_123", "presence": "online"})
            elif "user_456" in key:
                return json.dumps({"user_id": "user_456", "presence": "online"})
            return None
            
        mock_redis.get = AsyncMock(side_effect=mock_get)

        from app.services.presence_service import get_workspace_users

        result = await get_workspace_users("workspace_123", mock_redis)

        assert result is not None
        assert len(result) == 2
        assert result[0]["user_id"] == "user_123"

    async def test_remove_user_presence(self):
        """Test removing user presence from workspace."""
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock()

        await remove_user_presence("user_123", "workspace_123", mock_redis)

        assert mock_redis.delete.call_count == 3


@pytest.mark.asyncio
class TestOfflineMergeService:
    async def test_queue_offline_operations(self):
        """Test queuing offline operations for later sync."""
        mock_redis = AsyncMock()
        mock_lpush = AsyncMock()
        mock_redis.lpush = mock_lpush
        mock_redis.expire = AsyncMock()

        from app.services.offline_service import queue_offline_operations

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
            json.dumps({"type": "insert", "text": "Task 1", "position": 0}),
            json.dumps({"type": "insert", "text": "Task 2", "position": 1})
        ]

        mock_redis.lrange = mock_lrange

        from app.services.offline_service import get_queued_operations

        result = await get_queued_operations("user_123", "ydoc_abc", mock_redis)

        assert result is not None
        assert len(result) == 2
        assert result[0]["text"] == "Task 1"
        assert result[0]["position"] == 0

    async def test_clear_queued_operations(self):
        """Test clearing queued operations after sync."""
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)

        from app.services.offline_service import clear_queued_operations

        result = await clear_queued_operations("user_123", "ydoc_abc", mock_redis)

        assert result is True
        mock_redis.delete.assert_called_once_with("offline_ops:user_123:ydoc_abc")


class TestSocketEvents:
    def test_user_join_workspace(self):
        """Test user joining workspace room."""
        mock_socket_manager = MagicMock()

        with patch('app.services.socket_helpers.simple_socket_manager', mock_socket_manager):
            user_join_workspace(
                "user_123",
                "Alice",
                "workspace_123"
            )

        mock_socket_manager.join_room.assert_called_once_with("user_123", "workspace_123")

    def test_user_leave_workspace(self):
        """Test user leaving workspace room."""
        mock_socket_manager = MagicMock()

        with patch('app.services.socket_helpers.simple_socket_manager', mock_socket_manager):
            user_leave_workspace(
                "user_123",
                "workspace_123"
            )

        mock_socket_manager.leave_room.assert_called_once_with("user_123", "workspace_123")

    def test_broadcast_to_workspace(self):
        """Test broadcasting events to workspace members."""
        mock_socket_manager = MagicMock()

        with patch('app.services.socket_helpers.simple_socket_manager', mock_socket_manager):
            broadcast_to_workspace(
                "test_event",
                {"data": "test"},
                "workspace_123"
            )

        mock_socket_manager.broadcast.assert_called_once_with("test_event", "workspace_123", {"data": "test"})
