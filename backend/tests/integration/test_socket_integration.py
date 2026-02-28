"""
Integration Tests for Socket.IO Real-Time Collaboration

Written for Phase 5 of Task 1.2: Socket.IO Integration
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.api.socket_events import (
    sio_server,
    emit_task_created,
    emit_task_updated,
    emit_task_deleted,
    broadcast_crdt_update
)


@pytest.fixture
def mock_sio():
    """Create a mock Socket.IO server for testing."""
    mock_sio = MagicMock()
    return mock_sio


@pytest.mark.asyncio
class TestSocketIOHelpers:
    """Integration tests for Socket.IO helper functions."""

    async def test_emit_task_created(self, mock_sio):
        """Test: emit_task_created broadcasts to workspace."""
        task_data = {
            "task_id": "task_123",
            "title": "New Test Task",
            "workspace_id": "ws_456",
            "user_id": "user_123"
        }

        with patch('app.api.socket_events.sio_server', mock_sio):
            emit_task_created(task_data)

            mock_sio.emit.assert_called_once()
            call_args = mock_sio.emit.call_args
            assert call_args[0][0] == "task_created"
            assert call_args[1]["room"] == "ws_456"

    async def test_emit_task_updated(self, mock_sio):
        """Test: emit_task_updated broadcasts to workspace."""
        task_data = {
            "task_id": "task_123",
            "title": "Updated Task Title",
            "workspace_id": "ws_789",
            "user_id": "user_456"
        }

        with patch('app.api.socket_events.sio_server', mock_sio):
            emit_task_updated(task_data)

            mock_sio.emit.assert_called_once()
            call_args = mock_sio.emit.call_args
            assert call_args[0][0] == "task_updated"
            assert call_args[1]["room"] == "ws_789"

    async def test_emit_task_deleted(self, mock_sio):
        """Test: emit_task_deleted broadcasts to workspace."""
        task_data = {
            "task_id": "task_123",
            "title": "Task to Delete",
            "workspace_id": "ws_999",
            "user_id": "user_789"
        }

        with patch('app.api.socket_events.sio_server', mock_sio):
            emit_task_deleted(task_data)

            mock_sio.emit.assert_called_once()
            call_args = mock_sio.emit.call_args
            assert call_args[0][0] == "task_deleted"
            assert call_args[1]["room"] == "ws_999"
            assert "deleted_at" in call_args[0][1]

    async def test_broadcast_crdt_update(self, mock_sio):
        """Test: broadcast_crdt_update broadcasts to workspace."""
        workspace_id = "ws_222"
        crdt_data = {
            "doc_key": "ydoc_key_def",
            "operation": "update",
            "user_id": "user_222"
        }

        with patch('app.api.socket_events.sio_server', mock_sio):
            broadcast_crdt_update(workspace_id, crdt_data)

            mock_sio.emit.assert_called_once()
            call_args = mock_sio.emit.call_args
            assert call_args[0][0] == "crdt_update"
            assert call_args[1]["room"] == "ws_222"
            assert "updated_at" in call_args[0][1]

    async def test_emit_task_created_none_sio(self, mock_sio):
        """Test: Helper functions handle None sio_server gracefully."""
        task_data = {
            "task_id": "task_123",
            "workspace_id": "ws_456",
            "user_id": "user_123"
        }

        with patch('app.api.socket_events.sio_server', None):
            emit_task_created(task_data)
            # Should not raise an error

    async def test_broadcast_crdt_update_none_sio(self, mock_sio):
        """Test: broadcast_crdt_update handles None sio_server gracefully."""
        workspace_id = "ws_222"
        crdt_data = {
            "doc_key": "ydoc_key_def",
            "operation": "update",
            "user_id": "user_222"
        }

        with patch('app.api.socket_events.sio_server', None):
            broadcast_crdt_update(workspace_id, crdt_data)
            # Should not raise an error
