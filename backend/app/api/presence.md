# Presence Module

## Purpose
The Presence module tracks real-time user activity across workspaces, including online/offline status, typing indicators, and live cursor positions. It provides the "awareness" layer for multi-user collaboration.

## Public API
### REST Endpoints
- `GET /api/v1/presence/workspaces/{workspace_id}`: Get online users in a workspace.
- `POST /api/v1/presence/typing`: Manually update typing status (rare, usually via socket).
- `GET /api/v1/presence/typing/{workspace_id}`: List all currently typing users.
- `POST /api/v1/presence/cursor`: Submit a cursor position update.
- `GET /api/v1/presence/cursors/{workspace_id}`: Get global cursor map for a workspace.

### Socket Events
- `presence_update`: Informs workspace members when someone joins/leaves.
- `user_typing`: Broadcasts typing status changes.
- `cursor_moved`: Broadcasts high-frequency cursor position updates.

## Data Models
### UserPresence
- `user_id`: Target user.
- `user_name`: Display name.
- `presence`: Status string (online, away, offline).
- `cursor`: Object containing `{line, column, list_id, task_id}`.
- `last_seen`: ISO timestamp of the last activity heartbeat.

## Events Emitted/Consumed
- **Emitted**: `presence_update`, `user_typing`, `cursor_moved` (via SocketService).
- **Consumed**: `join_workspace`, `leave_workspace`, `cursor_position`, `start_typing`, `stop_typing` from clients.

## Invariants
- All presence data is ephemeral (cached in Redis).
- User keys expire after 5 minutes of inactivity (TTL).
- Typing indicators expire after 10 seconds of silence.

## Edge Cases
- **Zombie Connections**: Redis TTL ensures users are marked offline if the socket disconnects abruptly.
- **High-Frequency Cursors**: Cursors are broadcasted without database persistence to minimize latency.
- **Workspace Switching**: User presence is scoped to `workspace_id` to prevent cross-account leaks.

## Test Coverage
- Unit tests for Redis presence keys in `backend/tests/unit/test_presence_service.py`.
- Integration tests for presence broadcasts in `backend/tests/integration/test_presence_api.py`.
