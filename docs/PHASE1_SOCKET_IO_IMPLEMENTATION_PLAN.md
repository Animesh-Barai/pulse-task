# Task 1.2: Socket.IO Server Implementation Plan

## Executive Summary

Implement a fully functional Socket.IO server to enable real-time collaboration features in PulseTasks.

**Estimated Time:** 8-12 hours
**Priority:** 🔴 HIGH (blocks Week 2 completion)
**Dependencies:**
- ✅ Redis client initialized (from Task 1.1)
- ✅ FastAPI app structure (from Task 1.1)
- ✅ MongoDB database (from Task 1.1)
- ⏳ python-socketio library (need to install)
- ⏳ ASGI integration (need to implement)

---

## Current Status

### What's Already Done ✅

1. **FastAPI Application** - `backend/app/main.py` running
2. **MongoDB Connection** - `backend/app/db/database.py` connected
3. **Redis Configuration** - `REDIS_URL` configured in `backend/app/core/config.py`
4. **Docker Services** - Redis running on port 6379
5. **CRDT Service** - Document storage endpoints exist
6. **Presence Service** - Stub functions defined
7. **Test Infrastructure** - pytest working, 61/61 tests passing

### What's Missing ❌

1. **Socket.IO Server** - No `AsyncServer()` initialization
2. **Socket.IO Events** - No event handlers registered
3. **ASGI Integration** - Socket.IO not mounted on FastAPI
4. **Redis Client** - Not initialized (no `redis_client = redis.from_url()`)
5. **Real-time Events** - No connect/disconnect/join/leave handlers
6. **Presence Tracking** - Not connected to Socket.IO
7. **Cursor Broadcasting** - Not implemented
8. **CRDT Integration** - Not synced in real-time

---

## Implementation Plan

### Phase 1: Infrastructure Setup (2 hours)

#### 1.1 Initialize Redis Client

**File:** `backend/app/db/database.py`

```python
# Add Redis client initialization
import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client

# Add Redis health check
async def check_redis_health():
    try:
        return redis_client.ping() == b'PONG'
    except Exception as e:
        return False
```

**Testing:**
- Verify Redis connection
- Test ping/pong
- Check error handling

#### 1.2 Install python-socketio Dependencies

**File:** `backend/requirements.txt`

```
python-socketio[asyncio_client]==5.11.4
websockets==12.0
```

**Commands:**
```bash
.venv/Scripts/pip.exe install python-socketio[asyncio_client]
.venv/Scripts/pip.exe install websockets
```

**Validation:**
- Verify library installation
- Check version compatibility with FastAPI

---

### Phase 2: Socket.IO Server Setup (3 hours)

#### 2.1 Create Socket.IO Server

**File:** `backend/app/main.py`

```python
from socketio import ASGIApp, AsyncServer
from app.api.socket_events import register_socket_events

# Create Socket.IO server
sio = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create ASGI app
socket_app = ASGIApp(sio)

# Register all socket events
register_socket_events(sio)

# Mount Socket.IO on FastAPI
app.mount("/socket.io", socket_app)

# Socket.IO health check
@app.get("/health/socket")
async def socket_health():
    return {
        "status": "healthy",
        "server": "socketio",
        "async_mode": "asgi"
    }
```

#### 2.2 Create Socket Events Module

**File:** `backend/app/api/socket_events.py`

```python
from typing import Dict, Any
from socketio import AsyncServer
from app.db.database import get_redis
import json
import logging

logger = logging.getLogger(__name__)

def register_socket_events(sio: AsyncServer):
    """Register all Socket.IO event handlers."""

    @sio.event
    async def connect(sid: str, environ: Dict[str, Any]):
        """Handle client connection."""
        logger.info(f"Client connected: {sid}")
        # Store connection info
        await sio.save_session(sid, {
            "connected_at": datetime.utcnow().isoformat(),
            "user_id": environ.get("user_id"),
            "workspace_id": environ.get("workspace_id")
        })

    @sio.event
    async def disconnect(sid: str):
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {sid}")
        # Clean up presence
        redis = get_redis()
        redis.delete(f"presence:{sid}")

    @sio.event
    async def join_workspace(sid: str, data: Dict[str, Any]):
        """User joins a workspace."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")

        logger.info(f"User {user_id} joining workspace {workspace_id}")

        # Join socket room
        await sio.enter_room(sid, workspace_id)

        # Update presence in Redis
        redis = get_redis()
        redis.hset(
            f"workspace:{workspace_id}:presence",
            user_id,
            json.dumps({
                "sid": sid,
                "user_id": user_id,
                "name": data.get("user_name"),
                "joined_at": datetime.utcnow().isoformat()
            })
        )

        # Notify other users
        await sio.emit(
            "user_joined",
            {"user_id": user_id, "user_name": data.get("user_name")},
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def leave_workspace(sid: str, data: Dict[str, Any]):
        """User leaves a workspace."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")

        logger.info(f"User {user_id} leaving workspace {workspace_id}")

        # Leave socket room
        await sio.leave_room(sid, workspace_id)

        # Remove from Redis presence
        redis = get_redis()
        redis.hdel(f"workspace:{workspace_id}:presence", user_id)

        # Notify other users
        await sio.emit(
            "user_left",
            {"user_id": user_id, "user_name": data.get("user_name")},
            room=workspace_id
        )

    @sio.event
    async def cursor_position(sid: str, data: Dict[str, Any]):
        """Broadcast user's cursor position (collaboration)."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")
        list_id = data.get("list_id")

        # Store cursor position
        redis = get_redis()
        redis.hset(
            f"workspace:{workspace_id}:cursors",
            user_id,
            json.dumps({
                "list_id": list_id,
                "task_id": data.get("task_id"),
                "position": data.get("position"),
                "updated_at": datetime.utcnow().isoformat()
            })
        )

        # Broadcast to workspace
        await sio.emit(
            "cursor_moved",
            {
                "user_id": user_id,
                "list_id": list_id,
                "task_id": data.get("task_id"),
                "position": data.get("position")
            },
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def task_updated(sid: str, data: Dict[str, Any]):
        """Broadcast task update to all users in workspace."""
        workspace_id = data.get("workspace_id")
        task_id = data.get("task_id")

        logger.info(f"Task {task_id} updated in workspace {workspace_id}")

        # Broadcast update
        await sio.emit(
            "task_updated",
            data,
            room=workspace_id
        )

    @sio.event
    async def task_created(sid: str, data: Dict[str, Any]):
        """Broadcast new task creation to all users in workspace."""
        workspace_id = data.get("workspace_id")

        logger.info(f"Task created in workspace {workspace_id}")

        # Broadcast creation
        await sio.emit(
            "task_created",
            data,
            room=workspace_id
        )

    @sio.event
    async def task_deleted(sid: str, data: Dict[str, Any]):
        """Broadcast task deletion to all users in workspace."""
        workspace_id = data.get("workspace_id")
        task_id = data.get("task_id")

        logger.info(f"Task {task_id} deleted in workspace {workspace_id}")

        # Broadcast deletion
        await sio.emit(
            "task_deleted",
            data,
            room=workspace_id
        )

    @sio.event
    async def crdt_update(sid: str, data: Dict[str, Any]):
        """Receive and broadcast CRDT document updates."""
        workspace_id = data.get("workspace_id")
        doc_key = data.get("doc_key")

        logger.info(f"CRDT update for {doc_key} in workspace {workspace_id}")

        # Broadcast CRDT update to all users in workspace
        await sio.emit(
            "crdt_update",
            data,
            room=workspace_id,
            skip_sid=sid
        )
```

#### 2.3 Integrate with Existing API

**File:** `backend/app/api/tasks.py`

```python
# Add Socket.IO integration to task CRUD operations
from app.api.socket_events import sio

@router.post("/tasks")
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    # Create task in database
    new_task = await create_task_task(task, workspace_id=task.list_id)

    # Broadcast via Socket.IO
    await sio.emit(
        "task_created",
        {
            "task_id": new_task.id,
            "title": new_task.title,
            "user_id": current_user.id,
            "workspace_id": task.list_id
        },
        room=task.list_id
    )

    return new_task
```

---

### Phase 3: Presence Tracking (3 hours)

#### 3.1 Implement Presence Service

**File:** `backend/app/services/presence_service.py`

```python
from typing import List, Dict, Any
from app.db.database import get_redis
import json
import logging

logger = logging.getLogger(__name__)

async def get_workspace_presence(workspace_id: str) -> Dict[str, Any]:
    """Get all users present in a workspace."""
    redis = get_redis()

    # Get presence data from Redis
    presence_data = redis.hgetall(f"workspace:{workspace_id}:presence")

    # Parse JSON data
    users = {}
    for user_id_str, user_data in presence_data.items():
        users[user_id_str.decode()] = json.loads(user_data.decode())

    return {"users": users}

async def get_user_presence(user_id: str, workspace_id: str) -> Dict[str, Any]:
    """Get specific user's presence in a workspace."""
    redis = get_redis()

    # Get user presence
    user_data = redis.hget(f"workspace:{workspace_id}:presence", user_id)

    if user_data:
        return json.loads(user_data.decode())

    return None

async def update_user_presence(user_id: str, workspace_id: str, data: Dict[str, Any]):
    """Update user's presence in a workspace."""
    redis = get_redis()

    # Update presence data
    redis.hset(
        f"workspace:{workspace_id}:presence",
        user_id,
        json.dumps(data)
    )

    logger.info(f"Updated presence for user {user_id} in workspace {workspace_id}")
```

#### 3.2 Create Presence API Endpoints

**File:** `backend/app/api/presence.py`

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.services.presence_service import get_workspace_presence
from app.models.models import User

router = APIRouter(prefix="/api/v1/presence", tags=["presence"])

@router.get("/workspaces/{workspace_id}")
async def get_workspace_users(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all users currently present in a workspace."""
    return await get_workspace_presence(workspace_id)
```

---

### Phase 4: Integration with Existing Services (2 hours)

#### 4.1 Connect CRDT Service to Socket.IO

**File:** `backend/app/api/crdt.py`

```python
from app.api.socket_events import sio

# Update CRDT endpoints to broadcast changes
@router.post("/documents/{doc_key}")
async def save_crdt_document(doc_key: str, content: str, workspace_id: str):
    # Save to database
    await save_crdt_task(doc_key, content)

    # Broadcast update via Socket.IO
    await sio.emit(
        "crdt_update",
        {
            "doc_key": doc_key,
            "content": content,
            "workspace_id": workspace_id,
            "updated_at": datetime.utcnow().isoformat()
        },
        room=workspace_id
    )

    return {"status": "saved", "doc_key": doc_key}
```

---

### Phase 5: Testing (2 hours)

#### 5.1 Create Socket.IO Tests

**File:** `backend/tests/unit/test_socket_events.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.socket_events import register_socket_events
import socketio

@pytest.mark.asyncio
async def test_socket_connection():
    """Test Socket.IO connection handler."""
    mock_sio = MagicMock()

    register_socket_events(mock_sio)

    # Call connect handler
    await mock_sio.event('connect')('test_sid', {})

    # Verify session saved
    mock_sio.save_session.assert_called_once()

@pytest.mark.asyncio
async def test_join_workspace():
    """Test joining a workspace."""
    mock_sio = MagicMock()

    register_socket_events(mock_sio)

    # Simulate join
    await mock_sio.event('join_workspace')(
        'test_sid',
        {'workspace_id': 'ws_123', 'user_id': 'user_123'}
    )

    # Verify room joined
    mock_sio.enter_room.assert_called_once()

@pytest.mark.asyncio
async def test_cursor_position_broadcast():
    """Test cursor position broadcasting."""
    mock_sio = MagicMock()

    register_socket_events(mock_sio)

    # Simulate cursor move
    await mock_sio.event('cursor_position')(
        'test_sid',
        {'workspace_id': 'ws_123', 'user_id': 'user_123', 'position': 100}
    )

    # Verify broadcast
    mock_sio.emit.assert_called_once()

@pytest.mark.asyncio
async def test_task_update_broadcast():
    """Test task update broadcasting."""
    mock_sio = MagicMock()

    register_socket_events(mock_sio)

    # Simulate task update
    await mock_sio.event('task_updated')(
        'test_sid',
        {'workspace_id': 'ws_123', 'task_id': 'task_123', 'title': 'Updated Title'}
    )

    # Verify broadcast to room
    mock_sio.emit.assert_called_once_with(
        'task_updated',
        {'workspace_id': 'ws_123', 'task_id': 'task_123', 'title': 'Updated Title'},
        room='ws_123'
    )
```

#### 5.2 Integration Tests

**File:** `backend/tests/integration/test_socket_integration.py`

```python
import pytest
import socketio
import asyncio

@pytest.mark.asyncio
async def test_full_socket_flow():
    """Test complete real-time flow."""
    # Create Socket.IO client
    sio = socketio.AsyncClient()

    # Connect to server
    await sio.connect('http://localhost:8000/socket.io')

    # Join workspace
    await sio.emit('join_workspace', {'workspace_id': 'test_ws', 'user_id': 'user_123'})

    # Wait for confirmation
    await asyncio.sleep(0.5)

    # Update cursor position
    await sio.emit('cursor_position', {'workspace_id': 'test_ws', 'position': 50})

    # Disconnect
    await sio.disconnect()

    assert True  # If we get here, flow worked
```

---

## Deliverables

### Code Files to Create

1. ✅ `backend/app/db/database.py` - Add Redis client initialization
2. ✅ `backend/app/api/socket_events.py` - Socket.IO event handlers
3. ✅ `backend/app/services/presence_service.py` - Presence tracking logic
4. ✅ `backend/app/api/presence.py` - Presence API endpoints
5. ✅ `backend/tests/unit/test_socket_events.py` - Socket.IO unit tests
6. ✅ `backend/tests/integration/test_socket_integration.py` - Integration tests

### Code Files to Update

1. ✅ `backend/app/main.py` - Add Socket.IO server and ASGI mount
2. ✅ `backend/app/api/tasks.py` - Add Socket.IO broadcasts to task CRUD
3. ✅ `backend/app/api/crdt.py` - Add Socket.IO broadcasts to CRDT operations
4. ✅ `backend/requirements.txt` - Add python-socketio and websockets

### Documentation to Create

1. ✅ `docs/PHASE1_SOCKET_IO_IMPLEMENTATION.md` - Implementation report
2. ✅ `docs/SOCKET_IO_API.md` - Socket.IO API documentation for frontend

---

## Success Criteria

### Must Haves (Blocking)

- [ ] Socket.IO server running on `/socket.io` endpoint
- [ ] Redis client connected and working
- [ ] Connect/disconnect events working
- [ ] Join/leave workspace events working
- [ ] Presence tracking functional
- [ ] Cursor position broadcasting working
- [ ] Task updates broadcast in real-time
- [ ] All Socket.IO tests passing
- [ ] Integration tests passing

### Should Haves (Important)

- [ ] Error handling for Socket.IO events
- [ ] Logging for all Socket.IO operations
- [ ] Health check endpoint for Socket.IO
- [ ] Presence API endpoints functional
- [ ] Room-based broadcasting working
- [ ] User authentication integrated with Socket.IO

### Nice to Haves (Enhancement)

- [ ] Cursor history tracking
- [ ] Typing indicator (user is typing)
- [ ] Reconnection logic (auto-reconnect on disconnect)
- [ ] Message queuing (when disconnected)
- [ ] Performance metrics (connections, messages/sec)

---

## Testing Plan

### Unit Tests (Target: 90%+ coverage)

1. **Connection Tests**
   - Connect handler
   - Disconnect handler
   - Session management
   - Error handling

2. **Workspace Events Tests**
   - Join workspace
   - Leave workspace
   - Room management
   - Broadcasting

3. **Presence Tests**
   - User presence updates
   - Redis storage
   - Presence retrieval

4. **Cursor Tests**
   - Cursor position updates
   - Broadcasting
   - Redis storage

5. **Task Events Tests**
   - Task created broadcast
   - Task updated broadcast
   - Task deleted broadcast
   - Room-based routing

### Integration Tests

1. **End-to-End Flow**
   - Connect → Join → Update cursor → Disconnect
   - Multiple users in workspace
   - Real-time sync verification

2. **Performance Tests**
   - 10 concurrent users
   - 100 messages/second
   - Memory usage

3. **Error Scenarios**
   - Redis connection failure
   - Invalid workspace IDs
   - Network disconnections

---

## Risk Assessment

### 🔴 High Risks

1. **ASGI Integration Complexity**
   - **Risk:** FastAPI + Socket.IO ASGI compatibility issues
   - **Mitigation:** Use tested python-socketio version, follow official docs
   - **Fallback:** Separate Socket.IO server if ASGI fails

2. **Redis Connection Stability**
   - **Risk:** Redis connection drops, presence data lost
   - **Mitigation:** Add reconnection logic, persist critical data
   - **Monitoring:** Add Redis health checks

3. **Room Management**
   - **Risk:** Users in wrong rooms, data leakage
   - **Mitigation:** Validate workspace membership on every event
   - **Testing:** Extensive room join/leave testing

### 🟡 Medium Risks

1. **Memory Leaks**
   - **Risk:** Socket connections not properly closed
   - **Mitigation:** Explicit disconnect handling, resource cleanup
   - **Monitoring:** Track active connections

2. **Message Ordering**
   - **Risk:** Messages arrive out of order
   - **Mitigation:** Use sequence numbers in critical updates
   - **Testing:** Test high-frequency updates

3. **Authentication with Socket.IO**
   - **Risk:** Unauthorized users joining workspaces
   - **Mitigation:** Validate JWT tokens on connection
   - **Implementation:** Use Socket.IO middleware

---

## Dependencies

### Required Libraries

```txt
# backend/requirements.txt (add these)
python-socketio[asyncio_client]==5.11.4
websockets==12.0
```

### External Services

- ✅ Redis (already running on port 6379)
- ✅ MongoDB (already running on port 27017)
- ⏳ None (no additional services needed)

### Configuration

```python
# backend/app/core/config.py (already exists, verify these)
REDIS_URL: str = "redis://localhost:6379/0"  # ✅ Already configured
```

---

## Success Metrics

### Completion Metrics

- [ ] Socket.IO server running without errors
- [ ] All event handlers registered and tested
- [ ] Redis connection stable (no drops in 1 hour)
- [ ] Presence tracking working (users appear/disappear correctly)
- [ ] Cursor broadcasting working (real-time updates)
- [ ] Task CRUD updates broadcast instantly
- [ ] Unit tests passing (90%+)
- [ ] Integration tests passing (80%+)

### Performance Metrics

- [ ] < 50ms latency for Socket.IO events
- [ ] Support 100+ concurrent connections
- [ ] Handle 1000+ messages/second
- [ ] Memory usage < 200MB for 100 connections

### User Experience Metrics

- [ ] Users see each other join/leave instantly
- [ ] Cursor positions update smoothly
- [ ] No data loss during disconnections
- [ ] Real-time sync feels instant

---

## Timeline Breakdown

### Day 1 (4 hours)
- Initialize Redis client
- Install python-socketio
- Create basic Socket.IO server
- Test connection/disconnect

### Day 2 (4 hours)
- Implement workspace join/leave
- Add presence tracking
- Create presence API endpoints
- Test presence functionality

### Day 3 (2 hours)
- Implement cursor position broadcasting
- Add task update broadcasts
- Integrate with existing task API
- Test real-time updates

### Day 4 (2 hours)
- Write unit tests
- Write integration tests
- Fix any bugs found
- Final testing and validation

---

## Post-Implementation

### Immediate Follow-up

1. **Frontend Integration**
   - Provide Socket.IO client code
   - Document event names and data formats
   - Provide examples for React/Vue

2. **Documentation**
   - Update API documentation
   - Add Socket.IO architecture diagrams
   - Create troubleshooting guide

3. **Monitoring**
   - Add Socket.IO metrics (connections, messages)
   - Set up alerts for connection drops
   - Track Redis health

### Future Enhancements

1. **Advanced Presence**
   - User status (online, away, offline)
   - Typing indicators
   - Last seen timestamps

2. **CRDT Optimization**
   - Conflict resolution
   - Offline support
   - Delta updates (reduce bandwidth)

3. **Security**
   - Message encryption
   - Rate limiting
   - Input validation

---

## Approval Required

### ⚠️ Proceed to Implementation?

This plan requires your approval before proceeding with Task 1.2 implementation.

**Items to Confirm:**
1. ✅ Approach: Socket.IO server with Redis for presence tracking
2. ✅ Timeline: 4 days (8-12 hours total)
3. ✅ Deliverables: Socket.IO server, presence tracking, real-time updates
4. ✅ Testing: Unit + integration tests with 90%+ coverage

**Ready to proceed upon approval.**

---

**Created:** February 21, 2026
**Status:** 🟡 Awaiting Approval
**Owner:** Development Team
**Next:** Implement Socket.IO Server (Task 1.2)
