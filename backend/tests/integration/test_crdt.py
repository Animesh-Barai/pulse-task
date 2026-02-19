import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
class TestCRDTEndpoints:
    async def test_create_ydoc_success(self, client: AsyncClient):
        """Test creating a new Yjs document (list)."""
        mock_ydoc = {
            "id": "ydoc_123",
            "list_id": "list_123",
            "title": "My Task List",
            "y_doc_key": "doc_key_abc",
            "created_at": "2024-01-01T00:00:00"
        }

        with patch('app.api.crdt.create_ydoc', return_value=mock_ydoc):
            response = await client.post(
                "/api/v1/ydocs",
                json={
                    "list_id": "list_123",
                    "title": "My Task List"
                }
            )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "ydoc_123"
        assert data["y_doc_key"] == "doc_key_abc"

    async def test_get_ydoc_success(self, client: AsyncClient):
        """Test getting an existing Yjs document."""
        mock_ydoc = {
            "id": "ydoc_123",
            "list_id": "list_123",
            "title": "My Task List",
            "y_doc_key": "doc_key_abc"
        }

        with patch('app.api.crdt.get_ydoc', return_value=mock_ydoc):
            response = await client.get("/api/v1/ydocs/ydoc_123")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Task List"

    async def test_list_ydocs_by_workspace(self, client: AsyncClient):
        """Test listing Yjs documents by workspace."""
        mock_ydocs = [
            {"id": "ydoc_1", "title": "List 1", "list_id": "list_123"},
            {"id": "ydoc_2", "title": "List 2", "list_id": "list_123"}
        ]

        with patch('app.api.crdt.list_ydocs_by_workspace', return_value=mock_ydocs):
            response = await client.get("/api/v1/ydocs?workspace_id=workspace_123")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["list_id"] == "list_123"

    async def test_delete_ydoc_success(self, client: AsyncClient):
        """Test deleting a Yjs document."""
        mock_response = {"message": "Yjs document deleted"}

        with patch('app.api.crdt.delete_ydoc', return_value=True):
            response = await client.delete("/api/v1/ydocs/ydoc_123")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Yjs document deleted"


@pytest.mark.asyncio
class TestPresenceEndpoints:
    async def test_get_workspace_presence(self, client: AsyncClient):
        """Test getting online users in workspace."""
        mock_users = [
            {"user_id": "user_123", "name": "Alice", "status": "online"},
            {"user_id": "user_456", "name": "Bob", "status": "online"}
        ]

        with patch('app.api.crdt.get_workspace_presence', return_value=mock_users):
            response = await client.get("/api/v1/presence/workspace_123")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["status"] == "online"

    async def test_update_user_presence(self, client: AsyncClient):
        """Test updating user presence status."""
        mock_response = {"message": "Presence updated"}

        with patch('app.api.crdt.update_user_presence', return_value=True):
            response = await client.post(
                "/api/v1/presence",
                json={
                    "workspace_id": "workspace_123",
                    "status": "away"
                }
            )

        assert response.status_code == 200


@pytest.mark.asyncio
class TestSocketEndpoints:
    async def test_sync_ydoc_operations(self, client: AsyncClient):
        """Test syncing Yjs operations from client."""
        mock_operations = [
            {"type": "insert", "position": 0, "text": "Task 1"},
            {"type": "insert", "position": 1, "text": "Task 2"}
        ]

        with patch('app.api.crdt.sync_ydoc_operations', return_value=True):
            response = await client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": mock_operations}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["synced_count"] == 2

    async def test_get_ydoc_state(self, client: AsyncClient):
        """Test getting current Yjs document state."""
        mock_state = {
            "ydoc_key": "doc_key_abc",
            "compressed_state": "compressed_binary_data",
            "metadata": {"version": 123, "size": 2048}
        }

        with patch('app.api.crdt.get_ydoc_state', return_value=mock_state):
            response = await client.get("/api/v1/ydocs/state/doc_key_abc")

        assert response.status_code == 200
        data = response.json()
        assert "compressed_state" in data

    async def test_offline_operations_queue(self, client: AsyncClient):
        """Test queueing operations for offline editing."""
        mock_response = {"queued": 3, "ydoc_key": "doc_key_abc"}

        with patch('app.api.crdt.queue_offline_operations', return_value=mock_response):
            response = await client.post(
                "/api/v1/offline/queue",
                json={
                    "ydoc_key": "doc_key_abc",
                    "operations": [{"type": "insert", "text": "Offline task"}]
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["queued"] == 3

    async def test_sync_offline_operations(self, client: AsyncClient):
        """Test syncing queued offline operations."""
        mock_response = {"synced": 3, "success": True}

        with patch('app.api.crdt.sync_offline_operations', return_value=mock_response):
            response = await client.post("/api/v1/offline/sync/doc_key_abc")

        assert response.status_code == 200
        data = response.json()
        assert data["synced"] == 3


@pytest.mark.asyncio
class TestCRDTMergeScenarios:
    async def test_concurrent_edits_merge_success(self, client: AsyncClient):
        """Test that concurrent edits merge correctly."""
        # Simulate two users editing the same document
        operations_user1 = [
            {"type": "insert", "position": 0, "text": "User 1 task"}
        ]

        operations_user2 = [
            {"type": "insert", "position": 1, "text": "User 2 task"}
        ]

        with patch('app.api.crdt.apply_crdt_operations', return_value=True):
            # User 1 edits
            response1 = await client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": operations_user1}
            )
            assert response1.status_code == 200

            # User 2 edits (concurrent)
            response2 = await client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": operations_user2}
            )
            assert response2.status_code == 200

    async def test_offline_to_online_sync(self, client: AsyncClient):
        """Test syncing operations after user goes offline and back online."""
        # User goes offline, makes edits
        offline_ops = [
            {"type": "insert", "text": "Task created offline"},
            {"type": "update", "id": "task_1", "text": "Updated offline"}
        ]

        with patch('app.api.crdt.queue_offline_operations', return_value={"queued": 2}):
            queue_response = await client.post(
                "/api/v1/offline/queue",
                json={"operations": offline_ops}
            )
            assert queue_response.status_code == 200

        # User goes back online, syncs
        with patch('app.api.crdt.sync_offline_operations', return_value={"synced": 2}):
            sync_response = await client.post(
                "/api/v1/offline/sync/doc_key_abc"
            )
            assert sync_response.status_code == 200

    async def test_conflict_resolution(self, client: AsyncClient):
        """Test that CRDT handles conflicts automatically."""
        # CRDT should handle conflicts automatically, no manual resolution needed
        operations = [
            {"type": "insert", "position": 0, "text": "Task 1"},
            {"type": "insert", "position": 0, "text": "Task 1 (conflict)"}
        ]

        with patch('app.api.crdt.apply_crdt_operations', return_value=True):
            response = await client.post(
                "/api/v1/ydocs/sync/doc_key_abc",
                json={"operations": operations}
            )

        assert response.status_code == 200
        # Both operations should be preserved (CRDT property)
        data = response.json()
        assert data["operations_applied"] == 2
