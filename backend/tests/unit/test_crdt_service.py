import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.models.models import TaskList
from app.services.crdt_service import create_ydoc, get_ydoc
from app.services.presence_service import update_user_presence, remove_user_presence
from app.services.offline_service import queue_offline_operations
from app.services.socket_helpers import handle_ydoc_update, simple_socket_manager


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

        result = await create_ydoc(mock_db, "list_123", "My Task List")

        assert result is not None
        assert result.id == "ydoc_123"
        assert result.title == "My Task List"

    async def test_get_ydoc_exists(self):
        """Test getting an existing Yjs document."""
        mock_db = AsyncMock()
        mock_doc = TaskList(
            id="ydoc_123",
            list_id="list_123",
            title="My Task List",
            y_doc_key="doc_key_abc",
            created_at=datetime.utcnow()
        )

        mock_db.ydocs = MagicMock()
        mock_db.ydocs.find_one = AsyncMock(return_value=mock_doc)

        from app.services.crdt_service import get_ydoc
        result = await get_ydoc("ydoc_abc", mock_db)

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
            {"id": "ydoc_1", "title": "List 1", "list_id": "list_123"},
            {"id": "ydoc_2", "title": "List 2", "list_id": "list_123"}
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
        mock_set = AsyncMock()

        # Mock datetime.utcnow for TDD
        mock_datetime = MagicMock(return_value=datetime.utcnow())

        with patch('app.services.presence_service.update_user_presence', return_value=None):
            with patch('datetime.datetime', 'utcnow', return_value=mock_datetime):

                await update_user_presence(
                    "user_123",
                    "workspace_123",
                    "online",
                    mock_redis
                )

        mock_set.assert_called_once()
        # Verify 5-minute expiry
        mock_set.assert_called_with(
            key="presence:workspace_123:user_123",
            value=any,
            time=300
        )

    async def test_get_workspace_users(self):
        """Test getting all online users in workspace."""
        mock_redis = AsyncMock()
        mock_members = AsyncMock(return_value=[
            {"user_id": "user_123", "presence": "online"},
            {"user_id": "user_456", "presence": "online"}
        ])

        mock_redis.smembers = mock_members

        from app.services.presence_service import get_workspace_users

        result = await get_workspace_users("workspace_123", mock_redis)

        assert result is not None
        assert len(result) == 2
        assert result[0]["user_id"] == "user_123"

    async def test_remove_user_presence(self):
        """Test removing user presence from workspace."""
        mock_redis = AsyncMock()
        mock_delete = AsyncMock()

        with patch('app.services.presence_service.remove_user_presence', return_value=None):
            await remove_user_presence("user_123", "workspace_123", mock_redis)

        mock_delete.assert_called_once()


@pytest.mark.asyncio
class TestOfflineMergeService:
    async def test_queue_offline_operations(self):
        """Test queuing offline operations for later sync."""
        mock_redis = AsyncMock()
        mock_lpush = AsyncMock()

        # Mock datetime.utcnow for TDD
        mock_datetime = MagicMock(return_value=datetime.utcnow())

        mock_redis.lpush = mock_lpush

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
            {"type": "insert", "text": "Task 1", "position": 0},
            {"type": "insert", "text": "Task 2", "position": 1}
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
        mock_delete = AsyncMock()

        from app.services.offline_service import clear_queued_operations

        with patch('app.services.offline_service.clear_queued_operations', return_value=True):
            await clear_queued_operations("user_123", "ydoc_abc", mock_redis)

            mock_delete.assert_called_once()


@pytest.mark.asyncio
class TestSocketEvents:
    async def test_user_join_workspace(self):
        """Test user joining workspace room."""
        # Test expects sio_manager to be passed as second positional param
        mock_socket_manager = MagicMock()

        with patch('app.services.socket_helpers.simple_socket_manager', return_value=mock_socket_manager):

            await user_join_workspace(
                "user_123",
                "Alice",
                "workspace_123",
                mock_socket_manager
            )

        mock_socket_manager.join_room.assert_called_once_with("user_123", "workspace_123")

    async def test_user_leave_workspace(self):
        """Test user leaving workspace room."""
        # Test expects sio_manager as second positional param
        mock_socket_manager = MagicMock()

        with patch('app.services.socket_helpers.simple_socket_manager', return_value=mock_socket_manager):

            await user_leave_workspace(
                "user_123",
                "workspace_123",
                mock_socket_manager
            )

        mock_socket_manager.leave_room.assert_called_once_with("user_123", "workspace_123")

    async def test_broadcast_to_workspace(self):
        """Test broadcasting events to workspace members."""
        # Test expects sio_manager as second positional param
        mock_socket_manager = MagicMock()

        mock_broadcast = MagicMock()

        mock_socket_manager.broadcast = mock_broadcast

        with patch('app.services.socket_helpers.simple_socket_manager', return_value=mock_socket_manager):

            await broadcast_to_workspace(
                "test_event",
                {"data": "test"},
                "workspace_123",
                mock_socket_manager
            )

        mock_socket_manager.broadcast.assert_called_once_with("test_event", {"data": "test"}, "workspace_123")
