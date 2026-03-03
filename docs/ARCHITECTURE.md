# Architecture Documentation

Complete system architecture, data flows, and component interactions for PulseTasks.

---

## System Overview

PulseTasks is a real-time collaborative task management platform with AI-powered features. The architecture follows a microservices-like pattern with distinct components for authentication, task management, real-time collaboration, and AI suggestions.

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web App<br/>React/Next.js]
        MOBILE[Mobile App<br/>React Native]
    end

    subgraph "API Gateway Layer"
        FASTAPI[FastAPI<br/>REST API]
        SOCKET[Socket.IO<br/>Real-time]
    end

    subgraph "Service Layer"
        AUTH[Auth Service]
        TASK[Task Service]
        PRESENCE[Presence Service]
        CRDT[CRDT Service]
        AI[AI Service]
    end

    subgraph "Data Layer"
        MONGODB[(MongoDB<br/>Primary DB)]
        REDIS[(Redis<br/>Cache + Pub/Sub)]
        OPENAI[OpenAI API<br/>External AI]
    end

    WEB -->|REST| FASTAPI
    WEB -->|WebSocket| SOCKET
    MOBILE -->|REST| FASTAPI
    MOBILE -->|WebSocket| SOCKET

    FASTAPI --> AUTH
    FASTAPI --> TASK
    FASTAPI --> PRESENCE
    FASTAPI --> CRDT
    FASTAPI --> AI

    SOCKET --> PRESENCE
    SOCKET --> CRDT

    AUTH --> MONGODB
    AUTH --> REDIS

    TASK --> MONGODB
    TASK --> REDIS

    PRESENCE --> REDIS

    CRDT --> MONGODB
    CRDT --> REDIS

    AI --> OPENAI
    AI --> REDIS

    style FASTAPI fill:#3b82f6
    style SOCKET fill:#8b5cf6
    style MONGODB fill:#10b981
    style REDIS fill:#ef4444
    style OPENAI fill:#f59e0b
```

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Framework** | FastAPI | 0.109.0 | REST API framework |
| **WebSocket** | Python-SocketIO | 5.11.0 | Real-time communication |
| **ASGI Server** | Uvicorn | 0.27.0 | ASGI server |
| **Database** | MongoDB | 7.0 | Primary database |
| **Cache** | Redis | 7-alpine | Caching + Pub/Sub |
| **ORM** | Motor | 3.3.2 | Async MongoDB driver |
| **Authentication** | python-jose | 3.3.0 | JWT tokens |
| **Password Hashing** | Passlib | 1.7.4 | Bcrypt hashing |
| **HTTP Client** | httpx | 0.26.0 | Async HTTP requests |
| **Task Queue** | Celery | 5.3.6 | Background tasks |
| **AI Integration** | OpenAI API | Latest | AI suggestions |

### Frontend (Planned)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | React/Next.js | UI framework |
| **State Management** | Redux/Zustand | State management |
| **Real-time** | Socket.IO Client | Real-time updates |
| **CRDT** | Yjs | Conflict resolution |
| **HTTP Client** | Axios | API requests |

### DevOps

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Container management |
| **Orchestration** | Docker Compose | Multi-container setup |
| **Testing** | pytest | Unit/integration tests |
| **Code Quality** | Black, Flake8, mypy | Linting/type checking |
| **Monitoring** | Prometheus | Metrics collection |

---

## Data Flow Diagrams

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant AuthService
    participant MongoDB
    participant Redis

    Client->>FastAPI: POST /api/v1/auth/signup
    FastAPI->>AuthService: register(email, password)
    AuthService->>MongoDB: Check duplicate email
    MongoDB-->>AuthService: Email exists/doesn't exist

    alt Email already exists
        AuthService-->>FastAPI: Error: Email exists
        FastAPI-->>Client: 409 Conflict
    else Email available
        AuthService->>AuthService: Hash password (bcrypt)
        AuthService->>MongoDB: Create user document
        MongoDB-->>AuthService: User created
        AuthService->>AuthService: Generate JWT tokens
        AuthService->>Redis: Store refresh token
        AuthService-->>FastAPI: Success with tokens
        FastAPI-->>Client: 201 Created + tokens
    end

    Client->>FastAPI: POST /api/v1/auth/login
    FastAPI->>AuthService: login(email, password)
    AuthService->>MongoDB: Find user by email
    MongoDB-->>AuthService: User data
    AuthService->>AuthService: Verify password
    AuthService->>AuthService: Generate JWT tokens
    AuthService->>Redis: Store refresh token
    AuthService-->>FastAPI: Success with tokens
    FastAPI-->>Client: 200 OK + tokens
```

### Task Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant TaskService
    participant MongoDB
    participant AI
    participant Redis
    participant SocketIO

    Client->>FastAPI: POST /api/v1/tasks
    activate FastAPI
    FastAPI->>TaskService: create_task(data)
    activate TaskService

    TaskService->>MongoDB: Insert task document
    MongoDB-->>TaskService: Task created

    TaskService->>AI: suggest_task(title, description)
    activate AI
    AI->>AI: Generate suggestion
    AI->>Redis: Cache suggestion
    AI-->>TaskService: Suggestion data
    deactivate AI

    TaskService->>Redis: Publish task_created event
    TaskService-->>FastAPI: Task created
    deactivate TaskService

    FastAPI->>SocketIO: Broadcast task_created to workspace
    FastAPI-->>Client: 201 Created
    deactivate FastAPI

    Client-->>Client: Update UI with new task
```

### Real-Time Collaboration Flow

```mermaid
sequenceDiagram
    participant User1
    participant User2
    participant SocketIO
    participant PresenceService
    participant CRDTService
    participant Redis
    participant MongoDB

    User1->>SocketIO: Connect to workspace
    SocketIO->>PresenceService: set_presence(online)
    PresenceService->>Redis: Store presence
    PresenceService->>SocketIO: Broadcast presence_update
    SocketIO-->>User2: User1 is now online

    User1->>SocketIO: Update cursor position
    SocketIO->>PresenceService: update_cursor(x, y)
    PresenceService->>Redis: Store cursor
    PresenceService->>SocketIO: Broadcast cursor_updated
    SocketIO-->>User2: User1's cursor moved

    User1->>SocketIO: Edit task (Yjs update)
    SocketIO->>CRDTService: apply_yjs_update(update)
    CRDTService->>Redis: Publish crdt_update
    CRDTService->>MongoDB: Save Ydoc snapshot
    CRDTService-->>SocketIO: Update applied
    SocketIO-->>User2: Task updated (Yjs sync)

    Note over User1, User2: Both users see real-time changes
```

### AI Suggestion Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant AIService
    participant Redis
    participant OpenAI

    Client->>FastAPI: POST /ai/suggest/task
    FastAPI->>AIService: suggest_task(raw_title, context)

    AIService->>Redis: Check cache
    alt Cache hit
        Redis-->>AIService: Cached suggestion
        AIService-->>FastAPI: Suggestion from cache
    else Cache miss
        AIService->>OpenAI: Generate completion
        activate OpenAI
        OpenAI-->>AIService: AI response
        deactivate OpenAI
        AIService->>AIService: Parse and validate
        AIService->>Redis: Cache result
        AIService-->>FastAPI: AI suggestion
    end

    FastAPI-->>Client: 200 OK with suggestion

    Note over Client: User accepts/edits suggestion

    Client->>FastAPI: POST /ai/train/feedback
    FastAPI->>AIService: record_feedback(accepted, edits)
    AIService->>Redis: Store feedback for training
    AIService-->>FastAPI: Feedback recorded
    FastAPI-->>Client: 200 OK
```

---

## Component Interactions

### API Router Structure

```mermaid
graph LR
    subgraph "FastAPI Application"
        MAIN[main.py<br/>FastAPI App]

        subgraph "API Routers"
            AUTH[auth.router<br/>/api/v1/auth]
            TASK[tasks.router<br/>/api/v1/tasks]
            PRESENCE[presence.router<br/>/api/v1/presence]
            CRDT[crdt.router<br/>/api/v1/ydocs]
            AI[ai.router<br/>/ai]
        end

        subgraph "Socket.IO"
            SOCKET[socket_events.py<br/>Event Handlers]
        end
    end

    MAIN --> AUTH
    MAIN --> TASK
    MAIN --> PRESENCE
    MAIN --> CRDT
    MAIN --> AI
    MAIN --> SOCKET

    AUTH -->|Uses| AUTH_SVC[AuthService]
    TASK -->|Uses| TASK_SVC[TaskService]
    PRESENCE -->|Uses| PRES_SVC[PresenceService]
    CRDT -->|Uses| CRDT_SVC[CRDTService]
    AI -->|Uses| AI_SVC[AIService]

    SOCKET -->|Uses| PRES_SVC
    SOCKET -->|Uses| CRDT_SVC
```

### Service Layer Architecture

```mermaid
graph TB
    subgraph "Service Layer"
        AUTH_SVC[AuthService<br/>- User registration<br/>- Authentication<br/>- Token management]
        TASK_SVC[TaskService<br/>- CRUD operations<br/>- Filtering/sorting<br/>- Priority calculation]
        PRES_SVC[PresenceService<br/>- Online/offline status<br/>- Cursor tracking<br/>- Typing indicators]
        CRDT_SVC[CRDTService<br/>- Ydoc management<br/>- State synchronization<br/>- Conflict resolution]
        AI_SVC[AIService<br/>- Task suggestions<br/>- Prioritization<br/>- Feedback learning]
    end

    subgraph "Data Access Layer"
        MONGO_DB[MongoDB<br/>- Users<br/>- Tasks<br/>- Workspaces<br/>- Ydocs]
        REDIS_CACHE[Redis<br/>- Sessions<br/>- Presence<br/>- Rate limiting]
        REDIS_PUB[Redis<br/>- Pub/Sub<br/>- Real-time events]
    end

    AUTH_SVC --> MONGO_DB
    AUTH_SVC --> REDIS_CACHE

    TASK_SVC --> MONGO_DB
    TASK_SVC --> REDIS_CACHE

    PRES_SVC --> REDIS_CACHE
    PRES_SVC --> REDIS_PUB

    CRDT_SVC --> MONGO_DB
    CRDT_SVC --> REDIS_CACHE
    CRDT_SVC --> REDIS_PUB

    AI_SVC --> REDIS_CACHE
    AI_SVC -->|External| OPENAI[OpenAI API]
```

---

## Key Design Patterns

### 1. Dependency Injection

FastAPI's dependency injection for clean, testable code:

```python
# Example: Service injection
def get_task_service(db: AsyncIOMotorClient = Depends(get_database),
                    redis: Redis = Depends(get_redis)) -> TaskService:
    return TaskService(db.pulsetasks, redis)

@app.get("/api/v1/tasks")
async def get_tasks(service: TaskService = Depends(get_task_service)):
    return await service.get_tasks()
```

### 2. Repository Pattern

Abstract database operations behind service layer:

```python
class TaskService:
    def __init__(self, db: AsyncIOMotorDatabase, redis: Redis):
        self.db = db
        self.redis = redis

    async def create_task(self, task_data: TaskCreate) -> Task:
        # Business logic here
        task_dict = task_data.model_dump()
        result = await self.db.tasks.insert_one(task_dict)
        return Task(id=str(result.inserted_id), **task_dict)
```

### 3. Event-Driven Architecture

Redis Pub/Sub for real-time updates:

```python
# Publish events
async def publish_event(event_type: str, data: dict, workspace_id: str):
    await redis.publish(
        f"workspace:{workspace_id}",
        json.dumps({"event": event_type, "data": data})
    )

# Subscribe to events
@socketio.on("subscribe_workspace")
async def handle_subscribe(sid: str, workspace_id: str):
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"workspace:{workspace_id}")
    # ... handle incoming messages
```

### 4. Caching Strategy

Multi-level caching for performance:

```python
# L1: In-memory cache
# L2: Redis cache
# L3: Database

class AIService:
    async def suggest_task(self, raw_title: str, context: dict):
        cache_key = f"suggestion:{hash(raw_title + str(context))}"

        # Check Redis cache
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Call OpenAI API
        suggestion = await self._call_openai(raw_title, context)

        # Cache result (5 minutes)
        await self.redis.setex(cache_key, 300, json.dumps(suggestion))

        return suggestion
```

---

## Database Schema

### MongoDB Collections

#### Users Collection
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password_hash": "$2b$12$...",
  "name": "John Doe",
  "created_at": ISODate("2026-03-03T10:00:00Z"),
  "updated_at": ISODate("2026-03-03T10:00:00Z")
}
```

#### Tasks Collection
```json
{
  "_id": ObjectId,
  "title": "Implement feature",
  "description": "Description",
  "list_id": "list_abc123",
  "workspace_id": "ws_abc123",
  "assignee_id": "user_abc123",
  "priority": 3,
  "status": "OPEN",
  "due_date": ISODate("2026-03-10T12:00:00Z"),
  "tags": ["backend", "urgent"],
  "created_at": ISODate("2026-03-03T10:00:00Z"),
  "updated_at": ISODate("2026-03-03T10:00:00Z")
}
```

#### Ydocs Collection (CRDT Documents)
```json
{
  "_id": ObjectId,
  "list_id": "list_abc123",
  "title": "Task List",
  "y_doc_key": "ydoc_unique_key",
  "content": "<binary>",
  "created_at": ISODate("2026-03-03T10:00:00Z"),
  "updated_at": ISODate("2026-03-03T11:00:00Z")
}
```

### Redis Data Structures

#### Presence Data
```
key: presence:workspace:{workspace_id}
type: Hash
fields:
  - user_{user_id}: {"status": "online", "last_seen": timestamp}
```

#### Cursor Positions
```
key: cursor:workspace:{workspace_id}
type: Hash
fields:
  - user_{user_id}: {"x": 100, "y": 200, "task_id": "task_123"}
```

#### Rate Limiting
```
key: ratelimit:{workspace_id}:ai
type: String
value: "100" (requests in last 60s)
```

#### AI Cache
```
key: cache:ai:suggestion:{hash}
type: String
value: JSON-encoded suggestion
expiry: 300 seconds
```

---

## Security Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant FastAPI
    participant AuthService

    User->>Client: Enter credentials
    Client->>FastAPI: POST /auth/login
    FastAPI->>AuthService: Validate credentials
    AuthService-->>FastAPI: User authenticated
    FastAPI->>AuthService: Generate JWT tokens
    AuthService-->>FastAPI: access_token + refresh_token
    FastAPI-->>Client: Return tokens

    Note over Client: Store tokens securely

    Client->>FastAPI: GET /tasks (with Authorization header)
    FastAPI->>FastAPI: Validate JWT signature
    FastAPI-->>Client: Return protected data
```

### Security Layers

1. **Transport Layer**: HTTPS/TLS for all API calls
2. **Authentication**: JWT tokens with expiration
3. **Authorization**: Role-based access control (planned)
4. **Input Validation**: Pydantic models for request validation
5. **Rate Limiting**: Redis-based rate limiting per workspace
6. **CORS**: Configured for frontend domains only

---

## Scaling Strategy

### Horizontal Scaling

```mermaid
graph TB
    LB[Load Balancer<br/>Nginx]

    subgraph "Application Servers"
        APP1[FastAPI #1]
        APP2[FastAPI #2]
        APP3[FastAPI #3]
    end

    subgraph "Shared Services"
        MONGODB[(MongoDB<br/>Cluster)]
        REDIS[(Redis<br/>Cluster)]
    end

    LB --> APP1
    LB --> APP2
    LB --> APP3

    APP1 --> MONGODB
    APP2 --> MONGODB
    APP3 --> MONGODB

    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
```

### Caching Strategy

- **API Response Cache**: 5-60 seconds depending on endpoint
- **User Sessions**: Stored in Redis with TTL
- **AI Suggestions**: Cached with hash-based keys
- **Presence Data**: Fast lookup with minimal TTL (30 seconds)

### Database Scaling

- **Read Replicas**: For read-heavy operations
- **Sharding**: By workspace_id for multi-tenant scaling
- **Index Optimization**: All queries use indexed fields

---

## Monitoring and Observability

### Health Check Architecture

```mermaid
graph LR
    HEALTH[/health] --> API[API Service]
    HEALTH_SOCKET[/health/socket] --> SOCKET[Socket.IO Service]
    HEALTH_AI[/ai/health] --> AI[AI Service]

    API -->|Checks| DB[(MongoDB)]
    API -->|Checks| CACHE[(Redis)]

    SOCKET -->|Checks| CACHE

    AI -->|Checks| OPENAI[OpenAI API]
```

### Metrics to Monitor

| Metric | Type | Threshold |
|--------|------|-----------|
| API Response Time | Gauge | < 200ms (p95) |
| Error Rate | Counter | < 1% |
| Database Query Time | Histogram | < 100ms (p95) |
| Redis Latency | Histogram | < 10ms (p95) |
| AI Request Time | Histogram | < 3s (p95) |
| Socket.IO Connections | Gauge | Monitor trends |
| CPU Usage | Gauge | < 70% |
| Memory Usage | Gauge | < 80% |

---

## Future Enhancements

### Planned Features

1. **Message Queue**: RabbitMQ or AWS SQS for async tasks
2. **Search Engine**: Elasticsearch or Algolia for full-text search
3. **File Storage**: S3-compatible storage for attachments
4. **Webhook System**: External integrations (Slack, GitHub)
5. **Analytics**: Event tracking for user behavior
6. **Multi-tenancy**: Enhanced workspace isolation
7. **GraphQL**: Alternative to REST API (planned)

### Architecture Evolution

- **Microservices**: Split into separate services (auth, tasks, ai)
- **Event Sourcing**: Immutable event log for audit trail
- **CQRS**: Separate read/write models for complex queries

---

## Support

For architecture questions or improvements:
1. Review the sequence diagrams for component interactions
2. Check the service layer code for implementation details
3. Refer to API documentation for endpoint contracts

---

**Last Updated:** 2026-03-03
**Version:** 1.0.0
