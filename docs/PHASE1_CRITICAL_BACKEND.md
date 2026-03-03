# Phase 1: Critical Backend Implementation

**Status**: 🟡 **In Progress** (24-40 hours estimated)
**Duration**: 2-3 weeks
**Priority**: 🔴 **HIGH** (Blocks all advanced features)
**Owner**: Backend Development Team

---

## 📋 Executive Summary

Phase 1 focuses on completing the critical backend components that are currently blocking advanced features like real-time collaboration, AI-powered task rewriting, and background task processing. While the basic backend API is complete (FastAPI + MongoDB), the real-time infrastructure, AI microservice, and asynchronous processing systems are either missing or only partially implemented.

### Current State Analysis

| Component | Status | Completion | Blocking Issues |
|-----------|--------|------------|-----------------|
| **Basic Backend API** | ✅ Complete | 100% | None |
| **Authentication** | ✅ Complete | 100% | None |
| **Task Management API** | ✅ Complete | 100% | None |
| **Real-time (Socket.IO)** | ⚠️ Partial | 33% | Server not initialized |
| **Redis Integration** | ❌ Missing | 0% | Client not connected |
| **AI Microservice** | ❌ Missing | 0% | Empty directory |
| **Celery Workers** | ❌ Missing | 0% | Not configured |
| **Unit Tests** | ⚠️ Failing | 56% | 17 tests failing |

### Phase 1 Objectives

1. **Fix Unit Tests** - Get all 39 unit tests passing
2. **Implement Real-time Infrastructure** - Complete Socket.IO server and Redis integration
3. **Build AI MVP Service** - Implement task rewriting with OpenAI integration
4. **Set up Celery Workers** - Configure background job processing

**Success Criteria**:
- All 39 unit tests passing
- Real-time collaboration working between multiple clients
- AI task rewriting functional with confidence scoring
- Background jobs processing correctly
- Comprehensive test coverage (>80%)

---

## ✅ What's Already Done (Completed in Previous Phases)

### 1.1 Backend API Foundation ✅

**Files Implemented**:
- `backend/app/main.py` - FastAPI application entry point
- `backend/app/core/config.py` - Configuration management
- `backend/app/core/security.py` - JWT and password hashing
- `backend/app/db/database.py` - MongoDB connection management
- `backend/app/models/models.py` - Pydantic data models

**API Endpoints Implemented**:
```
✅ POST   /api/v1/auth/signup          - User registration
✅ POST   /api/v1/auth/login           - User login (JWT tokens)
✅ POST   /api/v1/auth/refresh         - Refresh JWT token
✅ POST   /api/v1/tasks                - Create new task
✅ GET    /api/v1/tasks/{id}           - Get task by ID
✅ GET    /api/v1/tasks                - List tasks with filters
✅ PUT    /api/v1/tasks/{id}           - Update task
✅ DELETE /api/v1/tasks/{id}           - Delete task
✅ GET    /api/v1/health               - Health check
```

**Integration Tests**: 16/16 passing (100%)

### 1.2 Authentication System ✅

**Features Implemented**:
- Email/password authentication
- JWT access tokens (30 min expiry)
- JWT refresh tokens (7 day expiry)
- Password hashing with bcrypt
- Protected route middleware
- User registration validation

**Test Coverage**: 83% (Phase 2 tutorial)

### 1.3 Docker Infrastructure ✅

**Services Running**:
```yaml
✅ MongoDB (port 27017) - Database
✅ Redis (port 6379) - Cache (not connected yet)
✅ Backend API (port 8000) - FastAPI server
```

**File**: `docker-compose.yml`

### 1.4 Test Infrastructure ✅

**Testing Tools Configured**:
- ✅ pytest with async support
- ✅ pytest-cov for coverage reports
- ✅ httpx for HTTP testing
- ✅ pytest.ini configuration

**Integration Tests**: 16/16 passing

### 1.5 Code Quality Tools ✅

**Tools Configured**:
- ✅ Black - Code formatting
- ✅ Flake8 - Linting
- ✅ mypy - Type checking
- ✅ isort - Import sorting

---

## ❌ What's Left to Implement

### Task 1.1: Fix Failing Unit Tests (3-5 hours) 🔴 CRITICAL

**Current State**:
- 22/39 unit tests passing (56%)
- 17/39 unit tests failing

**Failing Test Suites**:
```
❌ backend/tests/unit/test_auth_service.py    - 17/17 failing
❌ backend/tests/unit/test_task_service.py    - 13/13 failing
❌ backend/tests/unit/test_crdt_service.py    - 10/10 failing
```

**Root Cause**: Conftest incompatibility introduced in Phase 4.6
- AsyncClient vs TestClient pattern mismatch
- Fixture not loading correctly
- Mock not properly configured
- Test database not isolated

**Files to Fix**:
```python
backend/tests/conftest.py               # Fix fixture setup
backend/tests/unit/test_auth_service.py  # Fix auth tests
backend/tests/unit/test_task_service.py  # Fix task tests
backend/tests/unit/test_crdt_service.py  # Fix CRDT tests
```

**Required Changes**:

1. **Update conftest.py**:
```python
# backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.fixture
async def async_client():
    """Create async test client for all tests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_db():
    """Isolated test database"""
    # Setup test MongoDB connection
    # Clean up after each test
    yield db
    # Cleanup
```

2. **Fix Test Imports**:
```python
# Update all test files to use async_client
# Replace TestClient with AsyncClient
# Add async/await where needed
```

3. **Update Mock Configuration**:
```python
# Fix mock decorators
# Ensure proper patching of dependencies
```

**Deliverables**:
- ✅ All 39 unit tests passing
- ✅ Test isolation (no cross-test pollution)
- ✅ Coverage >80% for core modules

**Acceptance Criteria**:
```bash
pytest backend/tests/unit/ -v
# Expected: 39 passed, 0 failed
```

**Dependencies**: None

---

### Task 1.2: Implement Socket.IO Server (8-12 hours) 🔴 CRITICAL

**Current State**:
- `python-socketio` installed in requirements.txt
- `redis` installed but client not initialized
- No Socket.IO server instance in main.py
- No socket events registered

**What's Missing**:

#### 1.2.1 Initialize Redis Client

**File**: `backend/app/db/database.py` (modify)

**Current Code**:
```python
# backend/app/db/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)

def get_database():
    return client.pulsetasks
```

**Required Additions**:
```python
# Add to backend/app/db/database.py
import redis

# Initialize Redis client
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding='utf-8',
    decode_responses=True
)

def get_redis():
    """Get Redis client instance"""
    return redis_client
```

**Third-Party Credentials Required**:
```env
# .env file
REDIS_URL=redis://localhost:6379/0
# Optional: For production Redis (Cloud)
# REDIS_URL=redis://:password@redis-cloud-host:port/0
```

**Setup Instructions**:
```bash
# For local development (already in docker-compose.yml)
docker-compose up redis

# For production (Redis Cloud)
# 1. Sign up at https://redis.com/try-free/
# 2. Create database
# 3. Get connection string
# 4. Add to .env as REDIS_URL
```

#### 1.2.2 Create Socket.IO Server

**File**: `backend/app/main.py` (modify)

**Current Code**:
```python
# backend/app/main.py
from fastapi import FastAPI
from backend.app.api import auth, tasks

app = FastAPI(title="PulseTasks")
app.include_router(auth.router)
app.include_router(tasks.router)
```

**Required Additions**:
```python
# Add to backend/app/main.py
import socketio
from backend.app.db.database import get_redis
from backend.app.api.crdt import register_socket_events

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Get Redis client for message broker
redis_client = get_redis()

# Create Socket.IO manager with Redis
sio_manager = socketio.AsyncRedisManager(
    settings.REDIS_URL,
    pubsub='socketio'
)

# Attach Redis manager to server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    client_manager=sio_manager
)

# Create ASGI app for Socket.IO
socket_app = socketio.ASGIApp(sio)

# Mount Socket.IO to FastAPI
app.mount("/socket.io", socket_app)

# Register socket events
register_socket_events(sio)
```

#### 1.2.3 Register Socket Events

**File**: `backend/app/api/crdt.py` (modify)

**Current Code**:
```python
# backend/app/api/crdt.py
from fastapi import APIRouter
from backend.app.services.crdt_service import CRDTService

router = APIRouter(prefix="/api/v1/crdt", tags=["CRDT"])
crdt_service = CRDTService()

@router.post("/documents/{doc_id}")
async def create_document(doc_id: str):
    return crdt_service.create_document(doc_id)
```

**Required Additions**:
```python
# Add to backend/app/api/crdt.py
import socketio
from backend.app.services.presence_service import PresenceService
from backend.app.services.offline_service import OfflineService

presence_service = PresenceService()
offline_service = OfflineService()

def register_socket_events(sio: socketio.AsyncServer):
    """Register all Socket.IO event handlers"""

    @sio.event
    async def connect(sid, environ):
        """Client connects to Socket.IO"""
        print(f"Client connected: {sid}")
        # Verify auth token from environ
        auth_token = environ.get('HTTP_AUTHORIZATION')
        if not auth_token:
            return False  # Reject connection
        # Validate token and get user_id
        user_id = validate_token(auth_token)
        # Store user_id in session
        await sio.save_session(sid, {'user_id': user_id})

    @sio.event
    async def disconnect(sid):
        """Client disconnects"""
        print(f"Client disconnected: {sid}")
        session = await sio.get_session(sid)
        user_id = session.get('user_id')
        # Remove from all workspaces
        await presence_service.remove_user_all(user_id)

    @sio.event
    async def join_workspace(sid, data):
        """User joins a workspace"""
        workspace_id = data['workspace_id']
        session = await sio.get_session(sid)
        user_id = session['user_id']

        # Join socket.io room
        sio.enter_room(sid, workspace_id)

        # Update presence
        await presence_service.update_presence(
            user_id,
            workspace_id,
            'online'
        )

        # Broadcast presence update to workspace
        await sio.emit(
            'presence_update',
            {
                'user_id': user_id,
                'status': 'online',
                'workspace_id': workspace_id
            },
            room=workspace_id
        )

        # Send current room state to new user
        room_users = await presence_service.get_room_users(workspace_id)
        await sio.emit(
            'room_state',
            {'users': room_users},
            room=sid
        )

    @sio.event
    async def leave_workspace(sid, data):
        """User leaves a workspace"""
        workspace_id = data['workspace_id']
        session = await sio.get_session(sid)
        user_id = session['user_id']

        # Leave socket.io room
        sio.leave_room(sid, workspace_id)

        # Update presence
        await presence_service.update_presence(
            user_id,
            workspace_id,
            'offline'
        )

        # Broadcast presence update
        await sio.emit(
            'presence_update',
            {
                'user_id': user_id,
                'status': 'offline',
                'workspace_id': workspace_id
            },
            room=workspace_id
        )

    @sio.event
    async def cursor_update(sid, data):
        """User moves cursor in document"""
        workspace_id = data['workspace_id']
        document_id = data['document_id']
        session = await sio.get_session(sid)
        user_id = session['user_id']

        # Broadcast cursor to others in workspace
        await sio.emit(
            'cursor_update',
            {
                'user_id': user_id,
                'document_id': document_id,
                'position': data['position']
            },
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def typing_indicator(sid, data):
        """User typing indicator"""
        workspace_id = data['workspace_id']
        session = await sio.get_session(sid)
        user_id = session['user_id']

        # Broadcast typing status
        await sio.emit(
            'typing_indicator',
            {
                'user_id': user_id,
                'is_typing': data['is_typing']
            },
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def ydoc_sync(sid, data):
        """Yjs CRDT operations sync"""
        workspace_id = data['workspace_id']
        document_id = data['document_id']
        ops = data['ops']  # Binary CRDT operations

        # Store ops in database
        await crdt_service.save_ops(document_id, ops)

        # Broadcast to other users
        await sio.emit(
            'ydoc_update',
            {
                'document_id': document_id,
                'ops': ops
            },
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def task_update(sid, data):
        """Task update via socket (real-time)"""
        workspace_id = data['workspace_id']
        task_id = data['task_id']
        delta = data['delta']

        # Broadcast task update to workspace
        await sio.emit(
            'task_broadcast',
            {
                'task_id': task_id,
                'delta': delta
            },
            room=workspace_id,
            skip_sid=sid
        )
```

#### 1.2.4 Update Presence Service

**File**: `backend/app/services/presence_service.py` (currently has stubs)

**Required Implementation**:
```python
# backend/app/services/presence_service.py
from typing import Dict, List
from backend.app.db.database import get_redis
import json

class PresenceService:
    def __init__(self):
        self.redis = get_redis()

    async def update_presence(
        self,
        user_id: str,
        workspace_id: str,
        status: str
    ):
        """Update user presence status"""
        key = f"presence:{workspace_id}:{user_id}"
        value = {
            'user_id': user_id,
            'workspace_id': workspace_id,
            'status': status,
            'last_seen': str(datetime.utcnow())
        }
        await self.redis.hset(key, mapping=value)
        await self.redis.expire(key, 300)  # 5 min TTL

    async def get_room_users(self, workspace_id: str) -> List[Dict]:
        """Get all users in workspace"""
        pattern = f"presence:{workspace_id}:*"
        keys = await self.redis.keys(pattern)

        users = []
        for key in keys:
            user_data = await self.redis.hgetall(key)
            if user_data.get('status') == 'online':
                users.append(user_data)

        return users

    async def remove_user_all(self, user_id: str):
        """Remove user from all rooms"""
        pattern = f"presence:*:{user_id}"
        keys = await self.redis.keys(pattern)
        for key in keys:
            await self.redis.delete(key)
```

#### 1.2.5 Update Offline Service

**File**: `backend/app/services/offline_service.py` (currently empty)

**Required Implementation**:
```python
# backend/app/services/offline_service.py
from typing import List, Dict
from backend.app.db.database import get_redis
import json

class OfflineService:
    def __init__(self):
        self.redis = get_redis()

    async def queue_offline_ops(
        self,
        user_id: str,
        document_id: str,
        ops: bytes
    ):
        """Queue offline operations for sync"""
        key = f"offline:{user_id}:{document_id}"
        await self.redis.lpush(key, ops)
        await self.redis.expire(key, 86400)  # 24 hour TTL

    async def get_offline_ops(
        self,
        user_id: str,
        document_id: str
    ) -> List[bytes]:
        """Get queued offline operations"""
        key = f"offline:{user_id}:{document_id}"
        ops = await self.redis.lrange(key, 0, -1)
        await self.redis.delete(key)
        return ops

    async def merge_offline_ops(
        self,
        document_id: str,
        online_ops: List[bytes],
        offline_ops: List[bytes]
    ) -> List[bytes]:
        """Merge offline and online CRDT operations"""
        # Implement CRDT merge logic
        # Yjs handles this automatically, but we need to queue properly
        all_ops = offline_ops + online_ops
        return all_ops
```

**Deliverables**:
- ✅ Redis client initialized and connected
- ✅ Socket.IO server running
- ✅ Socket.IO events registered
- ✅ Presence tracking working
- ✅ Cursor positions synced
- ✅ Typing indicators working
- ✅ Yjs CRDT ops broadcasted
- ✅ Offline operation queue

**Acceptance Criteria**:
```bash
# Test 1: Socket.IO server starts
curl http://localhost:8000/socket.io/
# Expected: Socket.IO handshake response

# Test 2: Redis connection works
redis-cli ping
# Expected: PONG

# Test 3: Presence tracking works
# Connect two clients to same workspace
# Verify presence updates broadcasted
```

**Third-Party Credentials Required**:
```env
# Development (local)
REDIS_URL=redis://localhost:6379/0

# Production (Redis Cloud)
REDIS_URL=redis://:password@redis-host:port/0

# Get from: https://redis.com/try-free/
```

**Setup Instructions**:
1. **Local Development** (already configured):
   ```bash
   docker-compose up redis
   # Redis runs on localhost:6379
   ```

2. **Production Redis Cloud**:
   ```bash
   # 1. Create account at https://redis.com/try-free/
   # 2. Create database
   # 3. Copy connection string
   # 4. Add to .env:
   REDIS_URL=redis://:password@redis-host:port/0
   ```

**Dependencies**:
- Redis client initialized (Task 1.2.1)
- MongoDB connection (already exists)

**Estimated Time**: 8-12 hours

---

### Task 1.3: Build AI MVP Service (8-12 hours) 🔴 CRITICAL

**Current State**:
- `ai-service/` directory exists but is empty
- Dependencies configured in `ai-service/requirements.txt`
- No AI logic implemented
- No OpenAI integration
- No HTTP endpoints

**What's Missing**:

#### 1.3.1 Create AI Service Structure

**Directory Structure to Create**:
```
ai-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py          # Main AI logic
│   │   ├── heuristics.py          # Rule-based detection
│   │   └── classifier.py          # Local ML model
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── task_rewrite.py        # LLM prompts
│   └── workers/
│       ├── __init__.py
│       └── celery_worker.py        # Background jobs
├── requirements.txt               # Dependencies
├── Dockerfile                      # Container config
└── tests/
    ├── __init__.py
    └── test_ai_service.py         # Tests
```

#### 1.3.2 Create AI Service Configuration

**File**: `ai-service/app/core/config.py`

```python
# ai-service/app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """AI Service Configuration"""

    # App
    APP_NAME: str = "PulseTasks AI Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API Keys
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None

    # AI Settings
    ENABLE_CLOUD_LLM: bool = True
    CLOUD_LLM_MODEL: str = "gpt-4-turbo-preview"
    LOCAL_MODEL_THRESHOLD: float = 0.7  # Confidence threshold

    # Cache
    REDIS_URL: str = "redis://localhost:6379/1"
    CACHE_TTL: int = 3600  # 1 hour

    # Background Jobs
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"

settings = Settings()
```

#### 1.3.3 Create AI Data Models

**File**: `ai-service/app/models/schemas.py`

```python
# ai-service/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TaskRewriteRequest(BaseModel):
    """Request to rewrite a task"""
    raw_title: str = Field(..., min_length=1, max_length=200)
    raw_description: Optional[str] = Field(None, max_length=2000)
    context: Optional[dict] = None  # Workspace context

class ChecklistItem(BaseModel):
    """Single checklist item"""
    text: str
    completed: bool = False

class TaskRewriteResponse(BaseModel):
    """Response with AI suggestion"""
    rewritten_title: Optional[str] = None
    checklist: List[str] = []
    suggested_priority: Optional[int] = Field(None, ge=1, le=5)
    suggested_due_date: Optional[datetime] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str

class PriorityRequest(BaseModel):
    """Request to prioritize tasks"""
    task_ids: List[str] = []
    context: Optional[dict] = None

class PriorityResponse(BaseModel):
    """Response with prioritized tasks"""
    prioritized_tasks: List[dict] = []
    scores: List[float] = []

class FeedbackRequest(BaseModel):
    """User feedback on AI suggestion"""
    suggestion_id: str
    accepted: bool
    edit_distance: float = 0.0  # How much user edited
    user_id: str
```

#### 1.3.4 Implement Heuristics Engine

**File**: `ai-service/app/services/heuristics.py`

```python
# ai-service/app/services/heuristics.py
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class HeuristicsEngine:
    """Rule-based task analysis using heuristics"""

    # Priority keywords
    HIGH_PRIORITY_KEYWORDS = [
        'urgent', 'asap', 'critical', 'blocker', 'deadline',
        'today', 'tomorrow', 'immediately', 'important'
    ]

    # Time-based patterns
    TIME_PATTERNS = {
        'by friday': 5,
        'by monday': 1,
        'by wednesday': 3,
        'next week': 7,
        'end of month': 30,
        'asap': 1,
        'today': 0
    }

    # Task type patterns
    TASK_TYPES = {
        'bug': r'fix|bug|error|issue|crash',
        'feature': r'add|implement|create|build|new',
        'refactor': r'refactor|optimize|improve|clean',
        'documentation': r'document|doc|write|readme',
        'testing': r'test|qa|check|verify'
    }

    def analyze_task(self, title: str, description: str = "") -> Dict:
        """Analyze task using heuristics"""
        result = {
            'suggested_priority': None,
            'suggested_due_date': None,
            'task_type': None,
            'confidence': 0.6  # Base confidence for heuristics
        }

        # Extract priority
        result['suggested_priority'] = self._extract_priority(title, description)

        # Extract due date
        result['suggested_due_date'] = self._extract_due_date(title, description)

        # Extract task type
        result['task_type'] = self._extract_task_type(title)

        return result

    def _extract_priority(self, title: str, description: str) -> int:
        """Extract priority from text"""
        text = (title + " " + description).lower()

        # Check for high priority keywords
        for keyword in self.HIGH_PRIORITY_KEYWORDS:
            if keyword in text:
                return 5

        # Check for medium priority
        if any(word in text for word in ['important', 'soon', 'next']):
            return 3

        # Default priority
        return 2

    def _extract_due_date(self, title: str, description: str) -> Optional[datetime]:
        """Extract due date from text"""
        text = (title + " " + description).lower()

        # Check time patterns
        for pattern, days in self.TIME_PATTERNS.items():
            if pattern in text:
                due_date = datetime.now() + timedelta(days=days)
                return due_date

        return None

    def _extract_task_type(self, title: str) -> Optional[str]:
        """Extract task type from title"""
        title_lower = title.lower()

        for task_type, pattern in self.TASK_TYPES.items():
            if re.search(pattern, title_lower):
                return task_type

        return None

    def generate_checklist(self, task_type: str) -> List[str]:
        """Generate checklist based on task type"""
        checklists = {
            'bug': [
                'Reproduce the bug',
                'Identify root cause',
                'Write fix',
                'Test fix',
                'Add regression test',
                'Create pull request'
            ],
            'feature': [
                'Design solution',
                'Implement feature',
                'Write tests',
                'Update documentation',
                'Code review',
                'Merge to main'
            ],
            'refactor': [
                'Identify code to refactor',
                'Write tests for existing code',
                'Refactor code',
                'Run tests',
                'Code review'
            ],
            'documentation': [
                'Identify documentation gaps',
                'Write content',
                'Review content',
                'Update links',
                'Publish'
            ],
            'testing': [
                'Write test cases',
                'Execute tests',
                'Report results',
                'Fix issues found',
                'Re-test'
            ]
        }

        return checklists.get(task_type, ['Analyze requirements', 'Implement', 'Test'])
```

#### 1.3.5 Implement Local Classifier

**File**: `ai-service/app/services/classifier.py`

```python
# ai-service/app/services/classifier.py
from typing import Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class LocalClassifier:
    """Local ML classifier for task analysis"""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_model()

    def load_model(self):
        """Load pre-trained model or initialize"""
        model_path = 'ai-service/models/task_classifier.pkl'

        if os.path.exists(model_path):
            # Load existing model
            self.model = joblib.load(model_path)
            vectorizer_path = 'ai-service/models/vectorizer.pkl'
            self.vectorizer = joblib.load(vectorizer_path)
        else:
            # Initialize simple model (training would be done separately)
            self.model = RandomForestClassifier(n_estimators=100)
            self.vectorizer = TfidfVectorizer(max_features=1000)

    def classify_task(
        self,
        title: str,
        description: str = ""
    ) -> Dict:
        """Classify task using local model"""
        # Combine title and description
        text = f"{title} {description}"

        # For MVP, return mock classification
        # In production, this would use actual ML model
        confidence = 0.75  # Simulated confidence

        # Return classification result
        return {
            'task_type': 'feature',  # Mock result
            'priority': 3,  # Mock result
            'complexity': 'medium',  # Mock result
            'confidence': confidence
        }

    def train(self, texts: list, labels: list):
        """Train model on labeled data"""
        # Convert text to features
        X = self.vectorizer.fit_transform(texts)

        # Train model
        self.model.fit(X, labels)

        # Save model
        os.makedirs('ai-service/models', exist_ok=True)
        joblib.dump(self.model, 'ai-service/models/task_classifier.pkl')
        joblib.dump(self.vectorizer, 'ai-service/models/vectorizer.pkl')
```

#### 1.3.6 Implement AI Service

**File**: `ai-service/app/services/ai_service.py`

```python
# ai-service/app/services/ai_service.py
import json
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from backend.app.core.config import settings
from backend.app.services.heuristics import HeuristicsEngine
from backend.app.services.classifier import LocalClassifier
from backend.app.db.database import get_redis

class AIService:
    """Main AI service for task rewriting and suggestions"""

    def __init__(self):
        self.openai_client = None
        if settings.ENABLE_CLOUD_LLM and settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY
            )

        self.heuristics = HeuristicsEngine()
        self.classifier = LocalClassifier()
        self.redis = get_redis()

    async def rewrite_task(
        self,
        raw_title: str,
        raw_description: str = "",
        context: Optional[dict] = None
    ) -> Dict:
        """
        Rewrite task using AI

        Pipeline:
        1. Try heuristics (fast, <10ms)
        2. Try local classifier (fast, <50ms)
        3. Fall back to cloud LLM (slow, 1-2s)
        """
        # Check cache first
        cache_key = f"ai:rewrite:{hash(raw_title + str(context))}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Step 1: Try heuristics
        heuristics_result = self.heuristics.analyze_task(
            raw_title,
            raw_description
        )

        # Step 2: Try local classifier
        classifier_result = self.classifier.classify_task(
            raw_title,
            raw_description
        )

        # Step 3: If confidence low, use cloud LLM
        if (classifier_result['confidence'] < settings.LOCAL_MODEL_THRESHOLD
            and self.openai_client):

            llm_result = await self._call_cloud_llm(
                raw_title,
                raw_description,
                context
            )

            result = llm_result
        else:
            # Use heuristic + classifier results
            result = {
                'rewritten_title': heuristics_result.get('task_type') + ': ' + raw_title,
                'checklist': self.heuristics.generate_checklist(
                    heuristics_result.get('task_type', 'feature')
                ),
                'suggested_priority': heuristics_result['suggested_priority'],
                'suggested_due_date': heuristics_result['suggested_due_date'],
                'confidence': classifier_result['confidence'],
                'explanation': f"Detected {heuristics_result.get('task_type')} task"
            }

        # Cache result
        await self.redis.setex(
            cache_key,
            settings.CACHE_TTL,
            json.dumps(result)
        )

        return result

    async def _call_cloud_llm(
        self,
        title: str,
        description: str,
        context: Optional[dict] = None
    ) -> Dict:
        """Call OpenAI API for task rewriting"""
        from backend.app.prompts.task_rewrite import SYSTEM_PROMPT

        user_message = f"""
        Task Title: {title}
        Description: {description}
        Context: {json.dumps(context) if context else 'None'}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.CLOUD_LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Validate required fields
            if not all(key in result for key in [
                'rewritten_title', 'checklist', 'suggested_priority',
                'suggested_due_date', 'confidence', 'explanation'
            ]):
                raise ValueError("Invalid LLM response format")

            return result

        except Exception as e:
            # Fall back to heuristics on error
            return self.heuristics.analyze_task(title, description)

    async def prioritize_tasks(
        self,
        task_ids: List[str],
        context: Optional[dict] = None
    ) -> List[Dict]:
        """Prioritize tasks based on context"""
        # Implementation would consider:
        # - Deadlines
        # - Calendar availability
        # - Team velocity
        # - Current load

        # For MVP, return simple ranking
        prioritized = []
        for i, task_id in enumerate(task_ids):
            prioritized.append({
                'task_id': task_id,
                'priority': 5 - (i % 5),  # Simple mock ranking
                'score': (10 - i) / 10
            })

        return prioritized

    async def record_feedback(
        self,
        suggestion_id: str,
        accepted: bool,
        edit_distance: float,
        user_id: str
    ):
        """Record user feedback for learning"""
        feedback_data = {
            'suggestion_id': suggestion_id,
            'accepted': accepted,
            'edit_distance': edit_distance,
            'user_id': user_id,
            'timestamp': str(datetime.utcnow())
        }

        # Store in database for later training
        await self.redis.lpush('ai:feedback', json.dumps(feedback_data))
```

#### 1.3.7 Create LLM Prompts

**File**: `ai-service/app/prompts/task_rewrite.py`

```python
# ai-service/app/prompts/task_rewrite.py

SYSTEM_PROMPT = """
You are an AI assistant that rewrites ambiguous task titles into actionable, structured tasks.

Your task is to analyze the input task and output a JSON object with the following schema:

{
  "rewritten_title": "Clear, specific task title",
  "checklist": [
    "Specific actionable step 1",
    "Specific actionable step 2",
    "Specific actionable step 3"
  ],
  "suggested_priority": integer from 1 to 5,
  "suggested_due_date": "YYYY-MM-DD or null",
  "confidence": float from 0.0 to 1.0,
  "explanation": "Brief explanation of your reasoning"
}

Rules:
1. rewritten_title: Make it specific, actionable, and clear. Add context if helpful.
2. checklist: Generate 3-6 specific, actionable steps. Each step should be a complete action.
3. suggested_priority:
   - 1: Low priority, can wait
   - 2: Normal priority
   - 3: Medium-high priority
   - 4: High priority, important
   - 5: Critical, urgent, blocker
4. suggested_due_date: If you can infer a due date from context, use YYYY-MM-DD format. If uncertain, return null.
5. confidence: How confident are you in your suggestion? (0.0 to 1.0)
6. explanation: Briefly explain why you made these suggestions.

Important:
- Do NOT invent dates that aren't in the context. If no deadline is mentioned, return null for suggested_due_date.
- If the task is too vague to make good suggestions, set confidence low (<0.5) and say so in explanation.
- Checklist items should be specific and actionable, not generic.
- Always respond with valid JSON only, no free-form text.

Examples:

Input: "Fix landing page"
Output:
{
  "rewritten_title": "Fix landing page conversion rate issue",
  "checklist": [
    "Identify specific conversion issue on landing page",
    "Analyze user behavior and drop-off points",
    "Implement fix for identified issue",
    "Test changes in staging environment",
    "Monitor conversion rate after deployment"
  ],
  "suggested_priority": 4,
  "suggested_due_date": "2026-02-25",
  "confidence": 0.85,
  "explanation": "Task requires landing page analysis and optimization"
}

Input: "Meeting tomorrow"
Output:
{
  "rewritten_title": "Prepare for meeting tomorrow",
  "checklist": [
    "Review meeting agenda",
    "Prepare presentation slides",
    "Gather supporting documents",
    "Test meeting link"
  ],
  "suggested_priority": 4,
  "suggested_due_date": "2026-02-21",
  "confidence": 0.90,
  "explanation": "Tomorrow deadline detected, high priority preparation needed"
}

Input: "Write code"
Output:
{
  "rewritten_title": null,
  "checklist": [],
  "suggested_priority": null,
  "suggested_due_date": null,
  "confidence": 0.30,
  "explanation": "Task too vague - need more context about what code to write"
}
"""

USER_PROMPT_TEMPLATE = """
Analyze this task:

Task Title: {title}
Task Description: {description}
Context: {context}

Provide your analysis as JSON according to the schema.
"""
```

#### 1.3.8 Create FastAPI Endpoints

**File**: `ai-service/app/main.py`

```python
# ai-service/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.models.schemas import (
    TaskRewriteRequest,
    TaskRewriteResponse,
    PriorityRequest,
    PriorityResponse,
    FeedbackRequest
)
from backend.app.services.ai_service import AIService

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize AI service
ai_service = AIService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.post("/api/v1/ai/rewrite", response_model=TaskRewriteResponse)
async def rewrite_task(request: TaskRewriteRequest) -> TaskRewriteResponse:
    """
    Rewrite task using AI

    - Returns structured suggestion with confidence
    - Uses heuristics -> local classifier -> cloud LLM pipeline
    - Caches results in Redis
    """
    try:
        result = await ai_service.rewrite_task(
            raw_title=request.raw_title,
            raw_description=request.raw_description,
            context=request.context
        )
        return TaskRewriteResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/prioritize", response_model=PriorityResponse)
async def prioritize_tasks(request: PriorityRequest) -> PriorityResponse:
    """
    Prioritize tasks based on context

    - Considers deadlines, calendar, velocity, load
    - Returns prioritized list with scores
    """
    try:
        result = await ai_service.prioritize_tasks(
            task_ids=request.task_ids,
            context=request.context
        )
        return PriorityResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/feedback")
async def record_feedback(request: FeedbackRequest):
    """
    Record user feedback on AI suggestions

    - Used for learning and model improvement
    - Tracks acceptance/rejection rates
    """
    try:
        await ai_service.record_feedback(
            suggestion_id=request.suggestion_id,
            accepted=request.accepted,
            edit_distance=request.edit_distance,
            user_id=request.user_id
        )
        return {"status": "recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # AI service on port 8001
        reload=settings.DEBUG
    )
```

#### 1.3.9 Create AI Service Requirements

**File**: `ai-service/requirements.txt`

```txt
# ai-service/requirements.txt

# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# AI/ML
openai==1.10.0
scikit-learn==1.4.0
transformers==4.37.0
torch==2.1.2

# Data Processing
numpy==1.26.3
joblib==1.3.2

# Cache & Queue
redis==5.0.1
celery==5.3.6

# Utilities
python-dotenv==1.0.0
httpx==0.26.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

#### 1.3.10 Create AI Service Dockerfile

**File**: `ai-service/Dockerfile`

```dockerfile
# ai-service/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8001

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### 1.3.11 Integrate AI Service with Backend

**File**: `backend/app/api/ai.py` (create new)

```python
# backend/app/api/ai.py
from fastapi import APIRouter, Depends, HTTPException
import httpx
from backend.app.core.config import settings
from backend.app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

# AI service URL
AI_SERVICE_URL = settings.AI_SERVICE_URL or "http://ai-service:8001"

@router.post("/rewrite")
async def proxy_ai_rewrite(
    raw_title: str,
    raw_description: str = None,
    context: dict = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Proxy AI rewrite request to AI service

    - Forwards request to ai-service
    - Returns AI suggestion
    """
    try:
        payload = {
            "raw_title": raw_title,
            "raw_description": raw_description,
            "context": context
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/api/v1/ai/rewrite",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prioritize")
async def proxy_ai_prioritize(
    task_ids: list,
    context: dict = None,
    current_user: dict = Depends(get_current_user)
):
    """Proxy AI prioritize request to AI service"""
    try:
        payload = {
            "task_ids": task_ids,
            "context": context
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/api/v1/ai/prioritize",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Update backend/app/main.py**:
```python
# Add to backend/app/main.py
from backend.app.api import ai

app.include_router(ai.router)
```

**Update backend/app/core/config.py**:
```python
# Add to backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...

    # AI Service
    AI_SERVICE_URL: str = "http://ai-service:8001"
```

#### 1.3.12 Create Tests for AI Service

**File**: `ai-service/tests/test_ai_service.py`

```python
# ai-service/tests/test_ai_service.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_rewrite_task_simple(client):
    """Test task rewriting with simple input"""
    payload = {
        "raw_title": "Fix landing page",
        "raw_description": "Conversion rate is low",
        "context": {"workspace_type": "marketing"}
    }

    response = await client.post("/api/v1/ai/rewrite", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "rewritten_title" in data
    assert "checklist" in data
    assert "suggested_priority" in data
    assert "confidence" in data
    assert "explanation" in data

    # Validate types
    assert isinstance(data["checklist"], list)
    assert 1 <= data["suggested_priority"] <= 5
    assert 0.0 <= data["confidence"] <= 1.0

@pytest.mark.asyncio
async def test_rewrite_task_vague(client):
    """Test rewriting vague task"""
    payload = {
        "raw_title": "Write code",
        "raw_description": ""
    }

    response = await client.post("/api/v1/ai/rewrite", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Should have low confidence
    assert data["confidence"] < 0.5
    # Should explain vagueness
    assert "vague" in data["explanation"].lower()

@pytest.mark.asyncio
async def test_prioritize_tasks(client):
    """Test task prioritization"""
    payload = {
        "task_ids": ["task1", "task2", "task3"],
        "context": {}
    }

    response = await client.post("/api/v1/ai/prioritize", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "prioritized_tasks" in data
    assert "scores" in data
    assert len(data["prioritized_tasks"]) == 3
```

**Deliverables**:
- ✅ AI service FastAPI application
- ✅ Heuristics engine for fast suggestions
- ✅ Local classifier for medium complexity
- ✅ OpenAI integration for complex tasks
- ✅ Redis caching for performance
- ✅ Feedback loop for learning
- ✅ Comprehensive test suite
- ✅ Docker configuration

**Acceptance Criteria**:
```bash
# Test 1: AI service starts
docker-compose up ai-service
curl http://localhost:8001/health
# Expected: {"status":"healthy",...}

# Test 2: Task rewriting works
curl -X POST http://localhost:8001/api/v1/ai/rewrite \
  -H "Content-Type: application/json" \
  -d '{"raw_title":"Fix landing page"}'
# Expected: JSON with rewritten_title, checklist, etc.

# Test 3: Backend can call AI service
curl -X POST http://localhost:8000/api/v1/ai/rewrite \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"raw_title":"Fix landing page"}'
# Expected: Same AI response
```

**Third-Party Credentials Required**:
```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Get from: https://platform.openai.com/api-keys

# Optional: Google Cloud API (for alternative models)
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Get from: https://cloud.google.com/docs/authentication/api-keys

# Redis for caching (already configured)
REDIS_URL=redis://localhost:6379/1
```

**Setup Instructions**:

1. **Get OpenAI API Key**:
   ```bash
   # 1. Go to https://platform.openai.com/api-keys
   # 2. Create account (if needed)
   # 3. Generate new API key
   # 4. Copy key to clipboard
   # 5. Add to .env:
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx

   # Free tier: $5 credit
   # Paid: $0.01 per 1K tokens (GPT-4)
   # Estimated cost: $0.10-0.50 per day for 100 users
   ```

2. **Set Environment Variables**:
   ```bash
   # Add to .env file
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
   ENABLE_CLOUD_LLM=true
   AI_SERVICE_URL=http://ai-service:8001
   ```

3. **Start AI Service**:
   ```bash
   # Add to docker-compose.yml
   ai-service:
     build: ./ai-service
     ports:
       - "8001:8001"
     environment:
       - OPENAI_API_KEY=${OPENAI_API_KEY}
       - REDIS_URL=redis://redis:6379/1
     depends_on:
       - redis

   # Start service
   docker-compose up ai-service
   ```

**Dependencies**:
- Redis client initialized (Task 1.2.1)
- OpenAI API key
- Test infrastructure (already exists)

**Estimated Time**: 8-12 hours

---

### Task 1.4: Set up Celery Workers (4-8 hours) 🔴 CRITICAL

**Current State**:
- `celery` installed in requirements.txt
- No Celery app configured
- No worker tasks defined
- No job queue management

**What's Missing**:

#### 1.4.1 Create Celery Application

**File**: `backend/app/celery_app.py` (create new)

```python
# backend/app/celery_app.py
from celery import Celery
from backend.app.core.config import settings

# Create Celery app
celery_app = Celery(
    'pulsetasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'backend.app.workers.ai_tasks',
        'backend.app.workers.blocker_tasks',
        'backend.app.workers.notification_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'detect-blockers-every-5-minutes': {
        'task': 'backend.app.workers.blocker_tasks.detect_all_blockers',
        'schedule': 300.0,  # 5 minutes
    },
    'cleanup-old-suggestions': {
        'task': 'backend.app.workers.ai_tasks.cleanup_old_suggestions',
        'schedule': 86400.0,  # 24 hours
    },
}
```

**Update backend/app/core/config.py**:
```python
# Add to backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
```

#### 1.4.2 Create AI Worker Tasks

**File**: `backend/app/workers/ai_tasks.py` (create new)

```python
# backend/app/workers/ai_tasks.py
from backend.app.celery_app import celery_app
import httpx
from datetime import datetime, timedelta

@celery_app.task(name='process_ai_suggestion')
def process_ai_suggestion(task_id: str, raw_title: str, raw_description: str = ""):
    """
    Process AI suggestion for task

    - Calls AI service asynchronously
    - Stores suggestion in database
    - Notifies user via socket
    """
    try:
        # Call AI service
        with httpx.Client() as client:
            response = client.post(
                "http://ai-service:8001/api/v1/ai/rewrite",
                json={
                    "raw_title": raw_title,
                    "raw_description": raw_description
                },
                timeout=30.0
            )
            response.raise_for_status()
            suggestion = response.json()

        # Store suggestion in database
        # TODO: Implement database storage
        # suggestion_id = db.ai_suggestions.insert_one({
        #     "task_id": task_id,
        #     ...suggestion,
        #     "created_at": datetime.utcnow()
        # })

        # Notify user via socket
        # TODO: Emit socket event
        # socketio.emit('ai:suggestion', suggestion, room=user_id)

        return {
            "status": "success",
            "task_id": task_id,
            "suggestion": suggestion
        }

    except Exception as e:
        # Retry logic
        raise process_ai_suggestion.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(name='cleanup_old_suggestions')
def cleanup_old_suggestions():
    """
    Clean up old AI suggestions

    - Removes suggestions older than 7 days
    - Frees up database space
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        # TODO: Delete old suggestions from database
        # db.ai_suggestions.delete_many({
        #     "created_at": {"$lt": cutoff_date},
        #     "accepted": False
        # })

        return {
            "status": "success",
            "deleted_count": 0  # TODO: Return actual count
        }

    except Exception as e:
        raise cleanup_old_suggestions.retry(exc=e, countdown=3600, max_retries=3)

@celery_app.task(name='retrain_ai_model')
def retrain_ai_model():
    """
    Retrain AI model based on user feedback

    - Collects feedback from database
    - Retrains classifier
    - Updates model weights
    """
    try:
        # TODO: Implement retraining logic
        # 1. Collect feedback data
        # 2. Prepare training dataset
        # 3. Retrain model
        # 4. Save updated model

        return {
            "status": "success",
            "samples_used": 0  # TODO: Return actual count
        }

    except Exception as e:
        raise retrain_ai_model.retry(exc=e, countdown=3600, max_retries=2)
```

#### 1.4.3 Create Blocker Detection Tasks

**File**: `backend/app/workers/blocker_tasks.py` (create new)

```python
# backend/app/workers/blocker_tasks.py
from backend.app.celery_app import celery_app
import socketio
from typing import List, Dict
from datetime import datetime

# Socket.IO client for emitting notifications
sio = socketio.Client()

@celery_app.task(name='detect_all_blockers')
def detect_all_blockers():
    """
    Detect blockers for all active workspaces

    - Runs every 5 minutes (scheduled)
    - Analyzes tasks for implicit blockers
    - Notifies stakeholders
    """
    try:
        # TODO: Get all active workspaces
        workspaces = []  # db.workspaces.find({"active": True})

        blocked_count = 0

        for workspace_id in workspaces:
            result = detect_workspace_blockers(workspace_id)
            blocked_count += result['blocked_count']

        return {
            "status": "success",
            "workspaces_analyzed": len(workspaces),
            "blocked_tasks": blocked_count
        }

    except Exception as e:
        raise detect_all_blockers.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(name='detect_workspace_blockers')
def detect_workspace_blockers(workspace_id: str) -> Dict:
    """
    Detect blockers in specific workspace

    - Analyzes tasks for blockers
    - Emits notifications
    """
    try:
        # TODO: Get all tasks in workspace
        tasks = []  # db.tasks.find({"workspace_id": workspace_id})

        blocked_tasks = []

        for task in tasks:
            # Check for implicit blockers
            blockers = analyze_task_for_blockers(task)

            if blockers:
                blocked_tasks.append({
                    'task_id': str(task['_id']),
                    'task_title': task['title'],
                    'blockers': blockers
                })

                # Emit notification
                emit_blocker_notification(workspace_id, task, blockers)

        return {
            "status": "success",
            "workspace_id": workspace_id,
            "blocked_count": len(blocked_tasks)
        }

    except Exception as e:
        raise detect_workspace_blockers.retry(exc=e, countdown=30, max_retries=2)

def analyze_task_for_blockers(task: dict) -> List[str]:
    """Analyze single task for blockers"""
    blockers = []

    # Check 1: Status stuck in IN_PROGRESS too long
    if task.get('status') == 'IN_PROGRESS':
        days_in_progress = (datetime.utcnow() - task['updated_at']).days
        if days_in_progress > 7:
            blockers.append(f"Stuck in progress for {days_in_progress} days")

    # Check 2: Keywords in title/description
    text = (task.get('title', '') + ' ' + task.get('description', '')).lower()
    blocker_keywords = ['waiting for', 'depends on', 'blocked by', 'pending']
    for keyword in blocker_keywords:
        if keyword in text:
            blockers.append(f"Detected: '{keyword}'")

    # Check 3: Comments with blocker mentions
    # TODO: Analyze comments for blocker language

    return blockers

def emit_blocker_notification(
    workspace_id: str,
    task: dict,
    blockers: List[str]
):
    """Emit blocker notification to workspace"""
    try:
        # Connect to Socket.IO server
        sio.connect('http://backend:8000')

        # Emit notification
        sio.emit(
            'task_blocked',
            {
                'task_id': str(task['_id']),
                'task_title': task['title'],
                'workspace_id': workspace_id,
                'blockers': blockers,
                'confidence': 0.85,
                'suggested_action': 'Review blockers and unblock task'
            },
            room=workspace_id
        )

        sio.disconnect()

    except Exception as e:
        print(f"Failed to emit blocker notification: {e}")
```

#### 1.4.4 Create Notification Tasks

**File**: `backend/app/workers/notification_tasks.py` (create new)

```python
# backend/app/workers/notification_tasks.py
from backend.app.celery_app import celery_app
import socketio

# Socket.IO client
sio = socketio.Client()

@celery_app.task(name='send_task_notification')
def send_task_notification(
    user_id: str,
    workspace_id: str,
    notification_type: str,
    data: dict
):
    """
    Send task notification to user

    - Real-time via Socket.IO
    - Types: task_assigned, task_updated, task_completed, etc.
    """
    try:
        sio.connect('http://backend:8000')

        sio.emit(
            'task_notification',
            {
                'type': notification_type,
                'user_id': user_id,
                'workspace_id': workspace_id,
                'data': data,
                'timestamp': str(datetime.utcnow())
            },
            room=workspace_id
        )

        sio.disconnect()

        return {"status": "success"}

    except Exception as e:
        # Retry on connection failure
        raise send_task_notification.retry(exc=e, countdown=5, max_retries=3)

@celery_app.task(name='send_ai_suggestion_notification')
def send_ai_suggestion_notification(
    user_id: str,
    workspace_id: str,
    task_id: str,
    suggestion: dict
):
    """
    Send AI suggestion notification

    - Notifies user when suggestion is ready
    - Includes confidence score
    """
    try:
        sio.connect('http://backend:8000')

        sio.emit(
            'ai:suggestion',
            {
                'user_id': user_id,
                'workspace_id': workspace_id,
                'task_id': task_id,
                'suggestion': suggestion
            },
            room=workspace_id
        )

        sio.disconnect()

        return {"status": "success"}

    except Exception as e:
        raise send_ai_suggestion_notification.retry(exc=e, countdown=5, max_retries=3)

@celery_app.task(name='send_digest_email')
def send_digest_email(
    user_id: str,
    digest_type: str = 'daily'
):
    """
    Send digest email to user

    - Daily or weekly digest
    - Summarizes activity
    - TODO: Integrate email service
    """
    try:
        # TODO: Implement email sending
        # 1. Gather user activity
        # 2. Format digest
        # 3. Send via email service (SendGrid, etc.)

        return {
            "status": "success",
            "user_id": user_id,
            "digest_type": digest_type
        }

    except Exception as e:
        raise send_digest_email.retry(exc=e, countdown=300, max_retries=3)
```

#### 1.4.5 Update Docker Compose

**File**: `docker-compose.yml` (modify)

**Current docker-compose.yml**:
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
      MONGO_INITDB_DATABASE: pulsetasks

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**Required Additions**:
```yaml
# Add to docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
      MONGO_INITDB_DATABASE: pulsetasks

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://admin:password@mongodb:27017/pulsetasks?authSource=admin
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/2
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./backend:/app

  ai-service:
    build: ./ai-service
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379/1
      - CELERY_BROKER_URL=redis://redis:6379/2
    depends_on:
      - redis
    volumes:
      - ./ai-service:/app

  celery-worker:
    build: ./backend
    command: celery -A backend.app.celery_app worker --loglevel=info --concurrency=4
    environment:
      - MONGODB_URL=mongodb://admin:password@mongodb:27017/pulsetasks?authSource=admin
      - CELERY_BROKER_URL=redis://redis:6379/2
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - redis
      - mongodb
    volumes:
      - ./backend:/app

  celery-beat:
    build: ./backend
    command: celery -A backend.app.celery_app beat --loglevel=info
    environment:
      - MONGODB_URL=mongodb://admin:password@mongodb:27017/pulsetasks?authSource=admin
      - CELERY_BROKER_URL=redis://redis:6379/2
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - redis
    volumes:
      - ./backend:/app
```

#### 1.4.6 Create Worker Management Scripts

**File**: `scripts/start_workers.sh` (create new)

```bash
#!/bin/bash
# scripts/start_workers.sh

echo "Starting Celery workers..."

# Start worker
celery -A backend.app.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=1000 \
  -E

# Start beat (scheduler)
celery -A backend.app.celery_app beat \
  --loglevel=info
```

**File**: `scripts/monitor_workers.py` (create new)

```python
# scripts/monitor_workers.py
"""Monitor Celery workers and queue status"""
from celery import Celery
from redis import Redis
import json

# Create Celery app
celery_app = Celery('pulsetasks')
celery_app.conf.broker_url = 'redis://localhost:6379/2'

# Redis client
redis = Redis(host='localhost', port=6379, db=2)

def get_worker_stats():
    """Get worker statistics"""
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    active = inspect.active()

    return {
        'workers': len(stats) if stats else 0,
        'active_tasks': sum(len(tasks) for tasks in active.values()) if active else 0,
        'worker_details': stats
    }

def get_queue_stats():
    """Get queue statistics"""
    queue_length = redis.llen('celery')

    return {
        'queue_length': queue_length,
        'queue_name': 'celery'
    }

if __name__ == '__main__':
    print("=" * 50)
    print("Celery Worker Status")
    print("=" * 50)

    worker_stats = get_worker_stats()
    print(f"\nActive Workers: {worker_stats['workers']}")
    print(f"Active Tasks: {worker_stats['active_tasks']}")

    queue_stats = get_queue_stats()
    print(f"\nQueue Length: {queue_stats['queue_length']}")

    print("\n" + "=" * 50)
```

#### 1.4.7 Create Tests for Celery Tasks

**File**: `backend/tests/integration/test_celery_tasks.py` (create new)

```python
# backend/tests/integration/test_celery_tasks.py
import pytest
from backend.app.celery_app import celery_app
from backend.app.workers.ai_tasks import process_ai_suggestion

@pytest.mark.celery
def test_process_ai_suggestion_task():
    """Test AI suggestion processing task"""
    task = process_ai_suggestion.apply_async(
        args=['task_123', 'Fix landing page', 'Conversion rate is low']
    )

    # Wait for task to complete
    result = task.get(timeout=60)

    assert result['status'] == 'success'
    assert result['task_id'] == 'task_123'
    assert 'suggestion' in result

@pytest.mark.celery
def test_cleanup_old_suggestions_task():
    """Test cleanup old suggestions task"""
    from backend.app.workers.ai_tasks import cleanup_old_suggestions

    task = cleanup_old_suggestions.apply_async()
    result = task.get(timeout=60)

    assert result['status'] == 'success'
```

**Deliverables**:
- ✅ Celery application configured
- ✅ AI worker tasks (process suggestions, cleanup, retrain)
- ✅ Blocker detection worker tasks
- ✅ Notification worker tasks
- ✅ Worker and beat scheduler
- ✅ Docker compose updates
- ✅ Worker management scripts
- ✅ Tests for worker tasks

**Acceptance Criteria**:
```bash
# Test 1: Celery workers start
docker-compose up celery-worker celery-beat
# Expected: Workers running, processing tasks

# Test 2: Task executes successfully
python -c "from backend.app.celery_app import celery_app; \
from backend.app.workers.ai_tasks import process_ai_suggestion; \
task = process_ai_suggestion.apply_async(['task_1', 'Test']); print(task.get())"
# Expected: Task result returned

# Test 3: Periodic tasks running
celery -A backend.app.celery_app inspect active
# Expected: Scheduled tasks executing
```

**Third-Party Credentials Required**:
```env
# Redis for Celery broker (already configured)
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Production (Redis Cloud)
CELERY_BROKER_URL=redis://:password@redis-host:port/2
CELERY_RESULT_BACKEND=redis://:password@redis-host:port/2
```

**Setup Instructions**:
```bash
# 1. Add to .env
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 2. Start workers
docker-compose up celery-worker celery-beat

# 3. Monitor workers
python scripts/monitor_workers.py

# 4. View task queue
celery -A backend.app.celery_app inspect active
```

**Dependencies**:
- Redis client initialized (Task 1.2.1)
- MongoDB connection (already exists)
- AI service (Task 1.3)

**Estimated Time**: 4-8 hours

---

## 📊 Phase 1 Summary

### Total Estimated Effort: 24-40 hours

| Task | Description | Time | Priority |
|------|-------------|------|----------|
| 1.1 | Fix unit tests | 3-5h | 🔴 Critical |
| 1.2 | Socket.IO implementation | 8-12h | 🔴 Critical |
| 1.3 | AI service MVP | 8-12h | 🔴 Critical |
| 1.4 | Celery workers | 4-8h | 🔴 Critical |

### Third-Party Services Required

| Service | Purpose | Cost | Setup Time |
|---------|---------|------|------------|
| **OpenAI API** | AI task rewriting | $0.01-0.50/day | 5 min |
| **Redis Cloud** (optional) | Production cache | Free tier | 10 min |

### Third-Party Credentials Summary

```env
# Required for Phase 1

# OpenAI API Key (Required)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Get from: https://platform.openai.com/api-keys

# Redis URLs (Already configured in docker-compose)
REDIS_URL=redis://localhost:6379/0              # App cache
CELERY_BROKER_URL=redis://localhost:6379/2       # Job queue
CELERY_RESULT_BACKEND=redis://localhost:6379/2    # Job results

# Production Redis Cloud (Optional)
REDIS_URL=redis://:password@redis-host:port/0
CELERY_BROKER_URL=redis://:password@redis-host:port/2
```

### Deliverables

1. ✅ All 39 unit tests passing
2. ✅ Real-time collaboration working (Socket.IO + Redis)
3. ✅ AI task rewriting functional (OpenAI integration)
4. ✅ Background jobs processing (Celery workers)
5. ✅ Comprehensive test coverage (>80%)

### Success Criteria

- [ ] All 39 unit tests passing (100%)
- [ ] Socket.IO server handling real-time events
- [ ] AI service rewriting tasks with >70% confidence
- [ ] Celery workers processing background jobs
- [ ] Integration tests for all features passing

### Next Steps

After completing Phase 1, proceed to **Phase 2: Core Frontend Implementation** to build a working user interface that consumes these backend APIs.

---

**Document Version**: 1.0
**Last Updated**: February 20, 2026
**Next Review**: After Phase 1 completion
**Owner**: Backend Development Team
