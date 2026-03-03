# API Documentation

Complete reference for the PulseTasks REST API endpoints, authentication, and error handling.

---

## OpenAPI/Swagger Integration

### Accessing Interactive Documentation

FastAPI automatically generates interactive API documentation:

| Endpoint | Description |
|----------|-------------|
| `/docs` | Swagger UI - Interactive API explorer |
| `/redoc` | ReDoc - Alternative documentation viewer |
| `/openapi.json` | OpenAPI specification (JSON) |

### Using Bearer Token in Swagger

1. Navigate to `/docs`
2. Click **"Authorize"** button (top right)
3. Enter your JWT access token (without "Bearer " prefix)
4. Click **"Authorize"** to authenticate
5. All requests will include the token automatically

### Example: Testing Authenticated Endpoint

```bash
# Get your access token first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Response: {"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}

# Now use it in Swagger or curl
curl http://localhost:8000/api/v1/tasks?list_id=list_123 \
  -H "Authorization: Bearer eyJ..."
```

---

## Authentication API

Base URL: `/api/v1/auth`

All auth endpoints (except signup) require no authentication.

### POST /signup

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securePassword123"
}
```

**Response (201 Created):**
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-03-03T10:00:00Z"
}
```

**Errors:**
- `409 Conflict` - Email already registered
- `400 Bad Request` - Invalid email format or weak password

---

### POST /login

Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid email or password

**Token Expiry:**
- Access token: 15 minutes (default)
- Refresh token: 7 days (default)

---

### GET /me

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-03-03T10:00:00Z"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired token

---

### POST /refresh

Refresh an expired access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or revoked refresh token

**Note:** Old refresh token is revoked and a new one is issued.

---

### POST /logout

Revoke refresh token to logout user.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**Errors:**
- `400 Bad Request` - Invalid token format

---

## Tasks API

Base URL: `/api/v1/tasks`

All endpoints require Bearer token authentication.

### POST /

Create a new task. Triggers AI suggestion generation.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "title": "Implement user authentication",
  "description": "Add OAuth2 login support with Google and GitHub",
  "list_id": "list_abc123",
  "priority": 3,
  "status": "OPEN",
  "assignee_id": "user_def456",
  "due_date": "2026-03-10T12:00:00Z",
  "tags": ["backend", "auth"]
}
```

**Response (201 Created):**
```json
{
  "id": "task_ghi789",
  "title": "Implement user authentication",
  "description": "Add OAuth2 login support with Google and GitHub",
  "list_id": "list_abc123",
  "assignee_id": "user_def456",
  "priority": 3,
  "status": "OPEN",
  "due_date": "2026-03-10T12:00:00Z",
  "tags": ["backend", "auth"],
  "created_at": "2026-03-03T10:00:00Z",
  "updated_at": "2026-03-03T10:00:00Z"
}
```

**Socket.IO Event:** `task_created` broadcasted to workspace

**Errors:**
- `400 Bad Request` - Invalid task data
- `401 Unauthorized` - Invalid token

---

### GET /{task_id}

Get a single task by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "task_ghi789",
  "title": "Implement user authentication",
  "description": "Add OAuth2 login support",
  "list_id": "list_abc123",
  "assignee_id": "user_def456",
  "priority": 3,
  "status": "IN_PROGRESS",
  "due_date": "2026-03-10T12:00:00Z",
  "tags": ["backend", "auth"],
  "created_at": "2026-03-03T10:00:00Z",
  "updated_at": "2026-03-03T11:30:00Z"
}
```

**Errors:**
- `404 Not Found` - Task doesn't exist

---

### GET /

List tasks with optional filtering and sorting.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `list_id` | string | Yes | Filter by list ID |
| `status` | enum | No | Filter by status: OPEN, IN_PROGRESS, DONE |
| `priority` | enum | No | Filter by priority: 1-5 |
| `sort` | string | No | Sort field (e.g., "created_at", "priority") |
| `skip` | int | No | Number of results to skip (pagination) |
| `limit` | int | No | Maximum results to return |

**Example Request:**
```
GET /api/v1/tasks?list_id=list_abc&status=OPEN&priority=5&sort=-created_at&limit=10
```

**Response (200 OK):**
```json
[
  {
    "id": "task_ghi789",
    "title": "Implement user authentication",
    "description": "Add OAuth2 login support",
    "list_id": "list_abc123",
    "assignee_id": "user_def456",
    "priority": 5,
    "status": "OPEN",
    "due_date": "2026-03-10T12:00:00Z",
    "tags": ["backend", "auth"],
    "created_at": "2026-03-03T10:00:00Z",
    "updated_at": "2026-03-03T11:30:00Z"
  }
]
```

---

### PUT /{task_id}

Update an existing task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request (all fields optional):**
```json
{
  "title": "Implement user authentication with OAuth2",
  "description": "Updated description",
  "status": "IN_PROGRESS",
  "priority": 5,
  "assignee_id": "user_xyz789",
  "due_date": "2026-03-15T12:00:00Z",
  "tags": ["backend", "auth", "urgent"]
}
```

**Response (200 OK):**
```json
{
  "id": "task_ghi789",
  "title": "Implement user authentication with OAuth2",
  "description": "Updated description",
  "list_id": "list_abc123",
  "assignee_id": "user_xyz789",
  "priority": 5,
  "status": "IN_PROGRESS",
  "due_date": "2026-03-15T12:00:00Z",
  "tags": ["backend", "auth", "urgent"],
  "created_at": "2026-03-03T10:00:00Z",
  "updated_at": "2026-03-03T12:00:00Z"
}
```

**Socket.IO Event:** `task_updated` broadcasted to workspace

**Errors:**
- `404 Not Found` - Task doesn't exist

---

### DELETE /{task_id}

Delete a task permanently.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
```
(no response body)
```

**Socket.IO Event:** `task_deleted` broadcasted to workspace

**Errors:**
- `404 Not Found` - Task doesn't exist

---

## Presence API

Base URL: `/api/v1/presence`

Real-time presence tracking using Redis. All endpoints require Bearer token.

### GET /workspaces/{workspace_id}

Get all users with presence status in a workspace.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "workspace_id": "ws_abc123",
  "users": [
    {
      "user_id": "user_abc123",
      "user_name": "John Doe",
      "presence": "online",
      "cursor": {
        "list_id": "list_abc123",
        "task_id": "task_ghi789",
        "position": { "x": 100, "y": 200 }
      },
      "timestamp": 1740996000.0,
      "last_seen": "2 minutes ago"
    }
  ],
  "total_count": 1
}
```

**Presence Values:** `online`, `away`, `offline`

**Errors:**
- `503 Service Unavailable` - Redis not available

---

### POST /typing

Set or clear typing indicator for current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "workspace_id": "ws_abc123",
  "is_typing": true
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "is_typing": true
}
```

**Socket.IO Event:** `typing_updated` broadcasted to workspace

**Errors:**
- `503 Service Unavailable` - Redis not available

---

### GET /typing/{workspace_id}

Get list of users currently typing in workspace.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "workspace_id": "ws_abc123",
  "typing_users": ["user_abc123", "user_def456"]
}
```

**Errors:**
- `503 Service Unavailable` - Redis not available

---

### POST /cursor

Update cursor position for current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "workspace_id": "ws_abc123",
  "list_id": "list_abc123",
  "task_id": "task_ghi789",
  "position": {
    "x": 150,
    "y": 300,
    "selection": { "start": 0, "end": 10 }
  }
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "workspace_id": "ws_abc123",
  "position": { "x": 150, "y": 300 }
}
```

**Socket.IO Event:** `cursor_updated` broadcasted to workspace

**Errors:**
- `503 Service Unavailable` - Redis not available

---

### GET /cursors/{workspace_id}

Get cursor positions for all users in workspace.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "workspace_id": "ws_abc123",
  "cursor_positions": {
    "user_abc123": {
      "list_id": "list_abc123",
      "task_id": "task_ghi789",
      "position": { "x": 150, "y": 300 }
    },
    "user_def456": {
      "list_id": "list_abc123",
      "position": { "x": 200, "y": 400 }
    }
  }
}
```

**Errors:**
- `503 Service Unavailable` - Redis not available

---

### DELETE /users/{user_id}/workspaces/{workspace_id}

Remove user presence from workspace (called on disconnect/leave).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User user_abc123 removed from workspace ws_abc123"
}
```

**Errors:**
- `503 Service Unavailable` - Redis not available

---

## CRDT API (Yjs Documents)

Base URL: `/api/v1/ydocs`

CRDT document management for real-time collaboration. All endpoints require Bearer token.

### POST /

Create a new Yjs document (task list).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "list_id": "list_abc123",
  "title": "Backend Tasks"
}
```

**Response (201 Created):**
```json
{
  "id": "ydoc_abc123",
  "list_id": "list_abc123",
  "title": "Backend Tasks",
  "y_doc_key": "ydoc_abc123_unique_key",
  "created_at": "2026-03-03T10:00:00Z",
  "updated_at": null
}
```

**Socket.IO Event:** `task_created` broadcasted to workspace

---

### GET /{ydoc_key}

Get Yjs document metadata and state.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "ydoc_abc123",
  "list_id": "list_abc123",
  "title": "Backend Tasks",
  "y_doc_key": "ydoc_abc123_unique_key",
  "created_at": "2026-03-03T10:00:00Z",
  "updated_at": "2026-03-03T11:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Ydoc key not found

---

### GET /workspace/{workspace_id}

List all Yjs documents in a workspace.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "ydoc_abc123",
    "list_id": "list_abc123",
    "title": "Backend Tasks",
    "y_doc_key": "ydoc_abc123_unique_key",
    "created_at": "2026-03-03T10:00:00Z",
    "updated_at": "2026-03-03T11:00:00Z"
  }
]
```

---

### PUT /{ydoc_key}

Update Yjs document snapshot.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "content": "<binary Yjs state vector or encoded state>"
}
```

**Response (200 OK):**
```json
{
  "id": "ydoc_abc123",
  "list_id": "list_abc123",
  "title": "Backend Tasks",
  "y_doc_key": "ydoc_abc123_unique_key",
  "created_at": "2026-03-03T10:00:00Z",
  "updated_at": "2026-03-03T12:00:00Z"
}
```

**Socket.IO Event:** `crdt_update` broadcasted to workspace

**Errors:**
- `404 Not Found` - Ydoc key not found

---

### DELETE /{ydoc_key}

Delete Yjs document.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
```
(no response body)
```

**Socket.IO Event:** `crdt_update` broadcasted to workspace

**Errors:**
- `404 Not Found` - Ydoc key not found

---

## AI API

Base URL: `/ai`

AI-powered task suggestions and prioritization. Rate limited to **100 requests per 60 seconds per workspace**.

### POST /suggest/task

Generate AI-powered task suggestion with rewritten title, checklist, priority, and due date.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "raw_title": "Fix landing page",
  "raw_description": "Improve conversion rate",
  "context": {
    "workspace_id": "ws_abc123",
    "current_date": "2026-03-03T00:00:00Z",
    "workspace_type": "marketing"
  }
}
```

**Response (200 OK):**
```json
{
  "rewritten_title": "Improve landing page conversion rate (A/B test hero)",
  "checklist": [
    "Analyze funnel analytics to identify drop-off points",
    "Design hero section A & B variants",
    "Implement AB test and run for 2 weeks",
    "Collect metrics and decide winner"
  ],
  "suggested_priority": 2,
  "suggested_due_date": "2026-03-15",
  "confidence": 0.86,
  "explanation": "Detected marketing conversion intent + default 2-week testing cadence"
}
```

**Response (Low Confidence):**
```json
{
  "rewritten_title": null,
  "checklist": [],
  "suggested_priority": null,
  "suggested_due_date": null,
  "confidence": 0.23,
  "explanation": "Insufficient context: no workspace context or related historical tasks."
}
```

**Confidence Levels:**
- `≥ 0.8` - High confidence: Show inline suggestion
- `0.5 - 0.8` - Medium confidence: Show with "needs review"
- `< 0.5` - Low confidence: Store in background only

**Errors:**
- `429 Too Many Requests` - Rate limit exceeded (100/60s)
- `400 Bad Request` - Invalid input
- `500 Internal Server Error` - AI service error

**Caching:** Suggestions cached by hash of `raw_title + context` to reduce latency.

---

### POST /prioritize

Compute effective priority for tasks based on deadline, calendar, and team load.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "task_id": "task_abc123",
  "tasks": [
    {
      "id": "task_1",
      "title": "Fix critical bug",
      "priority": 5,
      "due_date": "2026-03-05"
    },
    {
      "id": "task_2",
      "title": "Add feature X",
      "priority": 3,
      "due_date": "2026-03-10"
    },
    {
      "id": "task_3",
      "title": "Documentation",
      "priority": 2,
      "due_date": null
    }
  ],
  "context": {
    "workspace_id": "ws_abc123",
    "current_date": "2026-03-03"
  }
}
```

**Response (200 OK):**
```json
{
  "prioritized_tasks": [
    {
      "id": "task_1",
      "title": "Fix critical bug",
      "priority": 5,
      "due_date": "2026-03-05"
    },
    {
      "id": "task_2",
      "title": "Add feature X",
      "priority": 3,
      "due_date": "2026-03-10"
    },
    {
      "id": "task_3",
      "title": "Documentation",
      "priority": 2,
      "due_date": null
    }
  ],
  "suggested_task_index": 0,
  "total_count": 3
}
```

**Priority Weight Calculation:**
- Priority weight: `priority * 100` (5 = 500, 1 = 100)
- Overdue weight: `+1000`
- Due date weight: `max(0, 30 - days_until_due)`
- Tasks sorted by total weight (descending)

**Errors:**
- `500 Internal Server Error` - Prioritization error

---

### POST /train/feedback

Record user feedback on AI suggestions for model training and telemetry.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "suggestion_id": "suggestion_abc123",
  "task_id": "task_def456",
  "user_id": "user_ghi789",
  "workspace_id": "ws_abc123",
  "accepted": true,
  "edit_distance": 0.1,
  "feedback_at": "2026-03-03T10:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "message": "Feedback recorded successfully",
  "recorded": true
}
```

**Feedback Used For:**
- Model retraining
- Confidence threshold tuning
- Workspace-level personalization

**Errors:**
- `500 Internal Server Error` - Feedback recording error

---

### GET /health

AI service health check.

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

---

## Authentication & Authorization

### Token-Based Authentication Flow

```
┌──────────┐                    ┌──────────┐
│  Client  │                    │   API    │
└────┬─────┘                    └────┬─────┘
     │                               │
     │ POST /auth/login              │
     ├──────────────────────────────>│
     │  {email, password}            │
     │                               │
     │ {access_token, refresh_token}│
     │<──────────────────────────────┤
     │                               │
     │ GET /api/v1/tasks             │
     │ Authorization: Bearer <token> │
     ├──────────────────────────────>│
     │                               │
     │ [tasks]                       │
     │<──────────────────────────────┤
     │                               │
     │ Token expires...              │
     │ POST /auth/refresh            │
     ├──────────────────────────────>│
     │ {refresh_token}               │
     │                               │
     │ {access_token, refresh_token}│
     │<──────────────────────────────┤
     └───────────────────────────────┘
```

### Using Bearer Tokens

**In curl:**
```bash
curl http://localhost:8000/api/v1/tasks?list_id=list_123 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**In JavaScript/Fetch:**
```javascript
fetch('http://localhost:8000/api/v1/tasks?list_id=list_123', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})
```

**In Python/requests:**
```python
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/v1/tasks?list_id=list_123', headers=headers)
```

### Token Refresh Mechanism

1. Access tokens expire after 15 minutes (configurable)
2. Use refresh token to get new access token without re-authentication
3. Old refresh token is revoked when new one is issued
4. Call `/auth/logout` to invalidate refresh token

**Automatic Refresh Pattern (Frontend):**
```javascript
async function fetchWithAuth(url, options = {}) {
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${getAccessToken()}`
    }
  });

  if (response.status === 401) {
    // Token expired, refresh it
    const newToken = await refreshToken();
    if (newToken) {
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`
        }
      });
    }
  }

  return response;
}
```

### Common Auth Errors

| Error | Description | Resolution |
|-------|-------------|------------|
| `401 Unauthorized` | Invalid or expired token | Refresh token or re-login |
| `401 Unauthorized` (detail: "Could not validate credentials") | Token format invalid | Check Bearer prefix |
| `401 Unauthorized` (detail: "Invalid or expired refresh token") | Refresh token revoked/expired | Re-login required |

---

## Error Codes Reference

### HTTP Status Codes

| Code | Name | When Used |
|------|------|-----------|
| **200** | OK | Successful GET, PUT, POST |
| **201** | Created | Successful resource creation |
| **204** | No Content | Successful DELETE (no body) |
| **400** | Bad Request | Invalid input data |
| **401** | Unauthorized | Missing/invalid authentication |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource already exists |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Unexpected server error |
| **503** | Service Unavailable | Redis/MongoDB not available |

### Error Response Format

**Standard Error:**
```json
{
  "detail": "Error message describing the issue"
}
```

**Validation Error (400):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Rate Limit Error (429):**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Auth Error (401):**
```json
{
  "detail": "Could not validate credentials",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

---

## Socket.IO Events

Real-time events broadcasted to workspaces:

### Task Events
| Event | Payload | Trigger |
|-------|---------|---------|
| `task_created` | `{task_id, title, workspace_id, user_id}` | Task created |
| `task_updated` | `{task_id, title, workspace_id, user_id}` | Task updated |
| `task_deleted` | `{task_id, title, workspace_id, user_id}` | Task deleted |

### Presence Events
| Event | Payload | Trigger |
|-------|---------|---------|
| `presence_update` | `{user_id, status}` | User presence changed |
| `typing_updated` | `{user_id, is_typing}` | User typing status changed |
| `cursor_updated` | `{user_id, position}` | User cursor moved |

### CRDT Events
| Event | Payload | Trigger |
|-------|---------|---------|
| `crdt_update` | `{doc_key, operation, user_id, content}` | Ydoc updated |

---

## Rate Limiting

### AI API Rate Limits

| Resource | Limit | Window | Scope |
|----------|-------|--------|-------|
| `/ai/suggest/task` | 100 requests | 60 seconds | Per workspace |

**Error Response:**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Rate Limit Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1740996660
```

---

## Health Check Endpoints

### GET /health

Check API service health.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "pulsetasks-backend",
  "socketio": "running"
}
```

### GET /health/socket

Check Socket.IO service health.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "server": "socketio",
  "async_mode": "asgi"
}
```

### GET /ai/health

Check AI service health.

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

---

## Complete Example Workflow

### 1. User Registration & Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "name": "John Doe",
    "password": "securePass123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securePass123"
  }'
```

**Save the `access_token` from response.**

---

### 2. Create a Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement API documentation",
    "description": "Write comprehensive API docs",
    "list_id": "list_abc123",
    "priority": 3,
    "status": "OPEN"
  }'
```

---

### 3. Get AI Suggestion for Task

```bash
curl -X POST http://localhost:8000/ai/suggest/task \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_title": "Implement API documentation",
    "raw_description": "Write comprehensive API docs",
    "context": {
      "workspace_id": "ws_abc123",
      "current_date": "2026-03-03T00:00:00Z"
    }
  }'
```

---

### 4. Update Task

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/task_ghi789 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "IN_PROGRESS",
    "priority": 5
  }'
```

---

### 5. Record Feedback on AI Suggestion

```bash
curl -X POST http://localhost:8000/ai/train/feedback \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "suggestion_id": "suggestion_abc123",
    "task_id": "task_ghi789",
    "user_id": "user_abc123",
    "workspace_id": "ws_abc123",
    "accepted": true,
    "edit_distance": 0.05
  }'
```

---

### 6. Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

### 7. Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

## Appendix: Data Models

### Task Priorities
| Value | Enum | Description |
|-------|------|-------------|
| 1 | LOW | Low priority |
| 2 | MEDIUM | Medium priority |
| 3 | HIGH | High priority |
| 4 | CRITICAL | Critical |
| 5 | URGENT | Urgent/Blocking |

### Task Statuses
| Value | Description |
|-------|-------------|
| OPEN | Task created, not started |
| IN_PROGRESS | Task is being worked on |
| DONE | Task completed |

### Presence States
| Value | Description |
|-------|-------------|
| online | User active in workspace |
| away | User inactive for >5 minutes |
| offline | User disconnected |

---

**Last Updated:** 2026-03-03
**API Version:** 1.0.0
