# CRDT Module

## Purpose
The CRDT module enables real-time, conflict-free collaborative editing for task lists and documents. It uses Yjs (ypy-websocket) to ensure that concurrent edits from multiple users merge deterministically without data loss.

## Public API
### REST Endpoints
- `POST /api/v1/ydocs/`: Create a new Yjs document (list).
- `GET /api/v1/ydocs/{ydoc_key}`: Fetch the current state/metadata of a Yjs document.
- `PUT /api/v1/ydocs/{ydoc_key}`: Manually update a document snapshot (rarely used, mainly for persistence).
- `GET /api/v1/ydocs/workspace/{workspace_id}`: List all collaborative documents in a workspace.

### Socket Events
- `ydoc_sync`: Binary event for exchanging Yjs update deltas.
- `crdt_update`: Broadcasted to notify peers of remote changes.
- `awareness_update`: Used for presence (cursors, typing).

## Data Models
### TaskList (YDoc)
- `id`: Internal MongoDB ID.
- `workspace_id`: Context for the document.
- `title`: Human-readable name.
- `y_doc_key`: Unique string used for synchronization routing.
- `yjs_state`: Binary blob of the CRDT state stored in MongoDB.

## Events Emitted/Consumed
- **Emitted**: `crdt_update`, `ydoc_sync` (via SocketIO).
- **Consumed**: `join_workspace`, `ydoc_sync` from clients.

## Invariants
- Each document must have a unique `y_doc_key`.
- Binary updates are append-only to ensure causality.
- Snapshots are taken periodically to reduce sync payload size.

## Edge Cases
- **Large Document Sync**: Large binary states are chunked or compressed.
- **Offline Triage**: Edits made while offline are merged immediately upon socket reconnection via the `ydoc_sync` protocol.
- **Conflict Resolution**: Deterministically handled by the Yjs engine on the client/server.

## Test Coverage
- Unit tests for state persistence in `backend/tests/unit/test_crdt_service.py`.
- Integration tests for real-time sync flows using `python-socketio` test clients.
