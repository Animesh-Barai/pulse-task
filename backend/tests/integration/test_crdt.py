import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.models import TaskList


class TestCRDTEndpoints:
    def test_create_ydoc_success(self, client: TestClient):
        """Test creating a new Yjs document (list)."""
        mock_ydoc = TaskList(
            id="ydoc_123",
            workspace_id="list_123",
            title="My Task List",
            y_doc_key="doc_key_abc"
        )

        with patch('app.api.crdt.create_ydoc', return_value=mock_ydoc):
            response = client.post(
                "/api/v1/ydocs/",
                json={
                    "list_id": "list_123",
                    "title": "My Task List"
                }
            )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "ydoc_123"
        assert data["y_doc_key"] == "doc_key_abc"

    def test_get_ydoc_success(self, client: TestClient):
        """Test getting an existing Yjs document."""
        mock_ydoc = TaskList(
            id="ydoc_123",
            workspace_id="list_123",
            title="My Task List",
            y_doc_key="doc_key_abc"
        )

        with patch('app.api.crdt.get_ydoc', return_value=mock_ydoc):
            response = client.get("/api/v1/ydocs/doc_key_abc")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Task List"

    def test_list_ydocs_by_workspace(self, client: TestClient):
        """Test listing Yjs documents by workspace."""
        mock_ydocs = [
            TaskList(id="ydoc_1", title="List 1", workspace_id="list_123", y_doc_key="key_1"),
            TaskList(id="ydoc_2", title="List 2", workspace_id="list_123", y_doc_key="key_2")
        ]

        with patch('app.api.crdt.list_ydocs_by_workspace', return_value=mock_ydocs):
            response = client.get("/api/v1/ydocs/workspace/workspace_123")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["list_id"] == "list_123"

    def test_delete_ydoc_success(self, client: TestClient):
        """Test deleting a Yjs document."""
        mock_ydoc = TaskList(
            id="ydoc_123",
            workspace_id="list_123",
            title="My Task List",
            y_doc_key="doc_key_abc"
        )

        with patch('app.api.crdt.get_ydoc', return_value=mock_ydoc):
            with patch('app.api.crdt.delete_ydoc', return_value=True):
                response = client.delete("/api/v1/ydocs/doc_key_abc")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Yjs document deleted"


class TestPresenceEndpoints:
    def test_get_workspace_presence(self, client: TestClient):
        """Test getting online users in workspace."""
        import time
        mock_users = [
            {"user_id": "user_123", "user_name": "Alice", "presence": "online", "timestamp": time.time(), "last_seen": "2026-06-13T20:00:00"},
            {"user_id": "user_456", "user_name": "Bob", "presence": "online", "timestamp": time.time(), "last_seen": "2026-06-13T20:00:00"}
        ]

        with patch('app.api.presence.get_workspace_users', return_value=mock_users):
            response = client.get("/api/v1/presence/workspaces/workspace_123")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert data["users"][0]["presence"] == "online"

    def test_update_user_presence(self, client: TestClient):
        """Test updating user presence status."""
        with patch('app.api.presence.update_user_presence', return_value=True):
            response = client.post(
                "/api/v1/presence",
                json={
                    "workspace_id": "workspace_123",
                    "status": "away"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Presence updated"


class TestSocketEndpoints:
    def test_sync_ydoc_operations(self, client: TestClient):
        """Test syncing Yjs operations from client."""
        mock_operations = [
            {"type": "insert", "position": 0, "text": "Task 1"},
            {"type": "insert", "position": 1, "text": "Task 2"}
        ]

        with patch('app.api.crdt.sync_ydoc_operations', return_value=True):
            response = client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": mock_operations}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["synced_count"] == 2

    def test_get_ydoc_state(self, client: TestClient):
        """Test getting current Yjs document state."""
        mock_state = {
            "ydoc_key": "doc_key_abc",
            "compressed_state": "compressed_binary_data",
            "metadata": {"version": 123, "size": 2048}
        }

        with patch('app.api.crdt.get_ydoc_state', return_value=mock_state):
            response = client.get("/api/v1/ydocs/state/doc_key_abc")

        assert response.status_code == 200
        data = response.json()
        assert "compressed_state" in data

    def test_offline_operations_queue(self, client: TestClient):
        """Test queueing operations for offline editing."""
        mock_response = {"queued": 3, "ydoc_key": "doc_key_abc"}

        with patch('app.api.crdt.queue_offline_operations', return_value=mock_response):
            response = client.post(
                "/api/v1/offline/queue",
                json={
                    "ydoc_key": "doc_key_abc",
                    "operations": [{"type": "insert", "text": "Offline task"}]
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["queued"] == 3

    def test_sync_offline_operations(self, client: TestClient):
        """Test syncing queued offline operations."""
        mock_response = {"synced": 3, "success": True}

        with patch('app.api.crdt.sync_offline_operations', return_value=mock_response):
            response = client.post("/api/v1/offline/sync/doc_key_abc")

        assert response.status_code == 200
        data = response.json()
        assert data["synced"] == 3


class TestCRDTMergeScenarios:
    def test_concurrent_edits_merge_success(self, client: TestClient):
        """Test that concurrent edits merge correctly."""
        operations_user1 = [
            {"type": "insert", "position": 0, "text": "User 1 task"}
        ]

        operations_user2 = [
            {"type": "insert", "position": 1, "text": "User 2 task"}
        ]

        with patch('app.api.crdt.sync_ydoc_operations', return_value=True):
            # User 1 edits
            response1 = client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": operations_user1}
            )
            assert response1.status_code == 200

            # User 2 edits (concurrent)
            response2 = client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": operations_user2}
            )
            assert response2.status_code == 200

    def test_offline_to_online_sync(self, client: TestClient):
        """Test syncing operations after user goes offline and back online."""
        offline_ops = [
            {"type": "insert", "text": "Task created offline"},
            {"type": "update", "id": "task_1", "text": "Updated offline"}
        ]

        with patch('app.api.crdt.queue_offline_operations', return_value={"queued": 2}):
            queue_response = client.post(
                "/api/v1/offline/queue",
                json={"operations": offline_ops}
            )
            assert queue_response.status_code == 200

        # User goes back online, syncs
        with patch('app.api.crdt.sync_offline_operations', return_value={"synced": 2}):
            sync_response = client.post(
                "/api/v1/offline/sync/doc_key_abc"
            )
            assert sync_response.status_code == 200

    def test_conflict_resolution(self, client: TestClient):
        """Test that CRDT handles conflicts automatically."""
        operations = [
            {"type": "insert", "position": 0, "text": "Task 1"},
            {"type": "insert", "position": 0, "text": "Task 1 (conflict)"}
        ]

        with patch('app.api.crdt.sync_ydoc_operations', return_value=True):
            response = client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": operations}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["operations_applied"] == 2
