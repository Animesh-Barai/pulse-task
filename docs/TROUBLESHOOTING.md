# Troubleshooting Guide

Common issues, error codes, debug tips, and solutions for PulseTasks.

---

## Quick Reference

| Issue Category | Common Solutions |
|----------------|------------------|
| **Database** | Check connection string, restart container, verify credentials |
| **Redis** | Check URL format, restart container, test with redis-cli |
| **Authentication** | Verify JWT secret, check token expiry, refresh token |
| **Real-time** | Check Socket.IO connection, verify Redis Pub/Sub |
| **API** | Check CORS settings, validate request data, check rate limits |

---

## Common Issues

### Database Issues

#### Issue 1: MongoDB Connection Failed

**Error Message:**
```
pymongo.errors.ConnectionFailure: Server selection timeout error
```

**Possible Causes:**
- MongoDB container not running
- Wrong connection string format
- Network connectivity issue
- Incorrect credentials

**Solutions:**

```bash
# 1. Check MongoDB container status
docker ps | grep mongo

# 2. Check MongoDB logs
docker compose logs mongodb

# 3. Restart MongoDB
docker compose restart mongodb

# 4. Test connection directly
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password

# 5. Verify connection string in .env
# MONGODB_URL=mongodb://admin:password@localhost:27017/pulsetasks?authSource=admin
```

**Expected Output:**
```
Current Mongosh Log ID: <id>
Connecting to: mongodb://<credentials>@localhost:27017/pulsetasks?authSource=admin&directConnection=true&serverSelectionTimeoutMS=2000
MongoDB server version: 7.0.x
```

---

#### Issue 2: Database Indexes Missing

**Error Message:**
```
pymongo.errors.DuplicateKeyError: E11000 duplicate key error collection
```

**Possible Causes:**
- Indexes not created during setup
- Database was reset without recreating indexes

**Solutions:**

```bash
# Connect to MongoDB
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password

# In MongoDB shell:
use pulsetasks

# Create indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.tasks.createIndex({ "list_id": 1 })
db.tasks.createIndex({ "assignee_id": 1 })
db.tasks.createIndex({ "status": 1 })
db.tasks.createIndex({ "due_date": 1 })
db.ydocs.createIndex({ "list_id": 1 }, { unique: true })
db.refresh_tokens.createIndex({ "token": 1 }, { unique: true })

# Verify indexes
db.users.getIndexes()
db.tasks.getIndexes()

exit
```

---

#### Issue 3: Slow Database Queries

**Symptoms:**
- API responses take > 1 second
- CPU usage high on MongoDB
- Queries showing in slow query log

**Solutions:**

```bash
# 1. Check MongoDB logs for slow queries
docker compose logs mongodb | grep "COMMAND"

# 2. Enable query profiling
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password
use pulsetasks
db.setProfilingLevel(2, { slowms: 100 })  # Log queries > 100ms

# 3. Analyze slow queries
db.system.profile.find().sort({ ts: -1 }).limit(5)

# 4. Explain query execution
db.tasks.find({ "list_id": "list_123" }).explain("executionStats")

# 5. Add missing indexes based on query patterns
db.tasks.createIndex({ "list_id": 1, "status": 1 })

exit
```

---

### Redis Issues

#### Issue 1: Redis Connection Failed

**Error Message:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Possible Causes:**
- Redis container not running
- Wrong connection URL format
- Redis binding to wrong interface

**Solutions:**

```bash
# 1. Check Redis container status
docker ps | grep redis

# 2. Check Redis logs
docker compose logs redis

# 3. Restart Redis
docker compose restart redis

# 4. Test connection with redis-cli
docker exec -it pulsetask-redis-1 redis-cli ping
# Expected: PONG

# 5. Verify connection string in .env
# REDIS_URL=redis://localhost:6379/0
```

---

#### Issue 2: Redis Out of Memory

**Error Message:**
```
OOM command not allowed when used memory > 'maxmemory'
```

**Possible Causes:**
- Too much data cached
- Memory limit too low
- Memory leak in application

**Solutions:**

```bash
# 1. Check Redis memory usage
docker exec -it pulsetask-redis-1 redis-cli INFO memory

# 2. Check memory usage by key
docker exec -it pulsetask-redis-1 redis-cli --bigkeys

# 3. Set memory eviction policy
docker exec -it pulsetask-redis-1 redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 4. Clear all cache (development only)
docker exec -it pulsetask-redis-1 redis-cli FLUSHALL

# 5. Update redis.conf for production (if needed)
# maxmemory 256mb
# maxmemory-policy allkeys-lru
```

---

### Authentication Issues

#### Issue 1: JWT Token Expired

**Error Message:**
```json
{
  "detail": "Could not validate credentials"
}
```

**Solutions:**

```bash
# 1. Get new access token with refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your-refresh-token"
  }'

# 2. If refresh token also expired, re-login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# 3. Check JWT settings in .env
# ACCESS_TOKEN_EXPIRE_MINUTES=15
# REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

#### Issue 2: Password Verification Failed

**Error Message:**
```
ValueError: Invalid password
```

**Solutions:**

```bash
# 1. Verify password is correct
# 2. Check if user exists in database
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password
use pulsetasks
db.users.find({ "email": "user@example.com" })

# 3. If needed, reset password (development only)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
new_hash = pwd_context.hash("newpassword123")

# 4. Update in database
db.users.updateOne(
  { "email": "user@example.com" },
  { "$set": { "password_hash": new_hash } }
)

exit
```

---

### Real-time Issues

#### Issue 1: Socket.IO Connection Failed

**Error Message:**
```
Connection error: Connection rejected
```

**Possible Causes:**
- Socket.IO server not running
- CORS misconfiguration
- Wrong socket.io endpoint

**Solutions:**

```bash
# 1. Check Socket.IO health
curl http://localhost:8000/health/socket

# Expected:
# {
#   "status": "healthy",
#   "server": "socketio",
#   "async_mode": "asgi"
# }

# 2. Check CORS settings in .env
# ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# 3. Verify frontend connection URL
# const socket = io("http://localhost:8000", {
#   transports: ["websocket"],
#   withCredentials: true
# });

# 4. Check backend logs for connection errors
docker compose logs backend | grep socketio
```

---

#### Issue 2: Real-time Updates Not Received

**Symptoms:**
- Task updates not showing in real-time
- Presence indicators not updating
- Cursor positions not syncing

**Solutions:**

```bash
# 1. Check Redis Pub/Sub
docker exec -it pulsetask-redis-1 redis-cli MONITOR

# 2. Check if events are being published
# (You should see events like:)
# 1712345678.123456 [0 redis] "PUBLISH" "workspace:ws_123" "{...}"

# 3. Check frontend subscription
# const socket = io("http://localhost:8000");
# socket.emit("join_workspace", { workspace_id: "ws_123" });

# 4. Verify Socket.IO event handlers
# backend/app/api/socket_events.py
```

---

### API Issues

#### Issue 1: CORS Errors

**Error Message (Browser Console):**
```
Access to fetch at 'http://localhost:8000/api/v1/tasks' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solutions:**

```bash
# 1. Check CORS settings in .env
# ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# 2. Check frontend URL configuration
# FRONTEND_URL=http://localhost:3000

# 3. Verify FastAPI CORS middleware
# backend/app/main.py
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[settings.FRONTEND_URL],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# 4. Restart backend after changing .env
docker compose restart backend
```

---

#### Issue 2: Rate Limit Exceeded

**Error Message:**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Solutions:**

```bash
# 1. Check rate limit status
curl -I http://localhost:8000/ai/suggest/task
# Headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 0
# X-RateLimit-Reset: 1740996660

# 2. Clear rate limit (development only)
docker exec -it pulsetask-redis-1 redis-cli DEL "ratelimit:ws_123:ai"

# 3. Wait for reset time
# (based on X-RateLimit-Reset timestamp)

# 4. Adjust rate limit in code (if needed)
# backend/app/api/ai.py
# @limiter.limit("100/60 seconds")  # Change as needed
```

---

## Debug Tips

### Enable Debug Logging

```bash
# 1. Set log level in .env
LOG_LEVEL=DEBUG

# 2. Restart backend
docker compose restart backend

# 3. View logs in real-time
docker compose logs -f backend

# 4. Filter logs by level
docker compose logs backend | grep DEBUG
docker compose logs backend | grep ERROR
```

### Use Python Debugger

```bash
# 1. Set breakpoint in code
# backend/app/services/auth_service.py
import pdb; pdb.set_trace()

# 2. Run tests in debug mode
pytest tests/ -v -s --pdb

# 3. Run server with debugger
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Use VS Code debugger
# See SETUP_GUIDE.md for launch.json configuration
```

### Check API Request/Response

```bash
# Use curl with verbose output
curl -v http://localhost:8000/api/v1/tasks?list_id=list_123 \
  -H "Authorization: Bearer your-token-here"

# Use httpie (install: pip install httpie)
http GET http://localhost:8000/api/v1/tasks?list_id=list_123 \
  Authorization:"Bearer your-token-here"

# Use Postman or Insomnia
# Import OpenAPI spec: http://localhost:8000/openapi.json
```

### Monitor Database Queries

```bash
# 1. Enable MongoDB profiler
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password
use pulsetasks
db.setProfilingLevel(2, { slowms: 0 })  # Log all queries

# 2. View recent queries
db.system.profile.find().sort({ ts: -1 }).limit(10)

# 3. Disable profiling (after debugging)
db.setProfilingLevel(0)

exit
```

---

## Error Codes

### HTTP Status Codes

| Code | Name | Description | Common Cause |
|------|------|-------------|--------------|
| 200 | OK | Success | Request completed successfully |
| 201 | Created | Resource created | POST request successful |
| 204 | No Content | Success, no body | DELETE request successful |
| 400 | Bad Request | Invalid input | Missing required fields, invalid data |
| 401 | Unauthorized | Authentication failed | Invalid/expired token, missing auth header |
| 404 | Not Found | Resource missing | Invalid ID, wrong endpoint |
| 409 | Conflict | Duplicate resource | Email already exists, duplicate key |
| 422 | Unprocessable Entity | Validation error | Pydantic validation failed |
| 429 | Too Many Requests | Rate limit exceeded | API rate limit hit |
| 500 | Internal Server Error | Server error | Unhandled exception |
| 503 | Service Unavailable | Dependency down | MongoDB/Redis not available |

### Application Error Details

#### 400 Bad Request

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

**Cause:** Missing required field in request body

**Fix:** Add all required fields to request

---

#### 401 Unauthorized - Invalid Token

```json
{
  "detail": "Could not validate credentials",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

**Cause:** Invalid or expired JWT token

**Fix:** Refresh token or re-login

---

#### 401 Unauthorized - Expired Refresh Token

```json
{
  "detail": "Invalid or expired refresh token"
}
```

**Cause:** Refresh token expired or revoked

**Fix:** Re-login to get new tokens

---

#### 409 Conflict - Duplicate Email

```json
{
  "detail": "Email already registered"
}
```

**Cause:** Attempting to register with existing email

**Fix:** Use different email or login with existing account

---

#### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Cause:** Exceeded API rate limit (100 requests/60s for AI endpoint)

**Fix:** Wait or clear rate limit (dev only)

---

#### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

**Cause:** Unhandled exception in backend code

**Fix:** Check logs for detailed error message

```bash
docker compose logs backend | tail -50
```

---

#### 503 Service Unavailable

```json
{
  "detail": "Service temporarily unavailable"
}
```

**Cause:** MongoDB or Redis not available

**Fix:** Check and restart services

```bash
docker ps
docker compose restart mongodb redis
```

---

## Performance Tuning

### Database Optimization

```bash
# 1. Create compound indexes for common queries
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password
use pulsetasks

# Index for tasks by list_id and status
db.tasks.createIndex({ "list_id": 1, "status": 1 })

# Index for tasks by assignee_id and priority
db.tasks.createIndex({ "assignee_id": 1, "priority": -1 })

# Index for tasks with due date
db.tasks.createIndex({ "due_date": 1 }, { sparse: true })

exit
```

### Redis Caching Strategy

```python
# backend/app/services/ai_service.py
import json
from datetime import timedelta

async def suggest_task(self, raw_title: str, context: dict):
    cache_key = f"suggestion:{hash(raw_title + str(context))}"

    # Check cache first
    cached = await self.redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Call OpenAI API
    suggestion = await self._call_openai(raw_title, context)

    # Cache with 5-minute TTL
    await self.redis.setex(
        cache_key,
        int(timedelta(minutes=5).total_seconds()),
        json.dumps(suggestion)
    )

    return suggestion
```

### Async Optimization

```python
# Use async/await for all I/O operations
async def get_task(self, task_id: str) -> Task:
    # Use async MongoDB driver (motor)
    task_doc = await self.db.tasks.find_one({"_id": ObjectId(task_id)})
    return Task(**task_doc)

# Parallel async operations
async def get_workspace_tasks(self, workspace_id: str):
    tasks = await self.db.tasks.find({"workspace_id": workspace_id}).to_list(length=None)
    presence = await self.redis.get(f"presence:workspace:{workspace_id}")
    return tasks, presence
```

### Connection Pooling

```python
# backend/app/db/database.py
from motor.motor_asyncio import AsyncIOMotorClient

# Configure connection pool
mongodb_client = AsyncIOMotorClient(
    settings.MONGODB_URL,
    maxPoolSize=50,      # Max connections in pool
    minPoolSize=5,        # Min connections to maintain
    maxIdleTimeMS=30000,  # Close idle connections after 30s
    connectTimeoutMS=5000 # Connection timeout
)
```

---

## Security Issues

### Issue: Weak JWT Secret

**Problem:** Using default or predictable JWT secret key

**Solution:**
```bash
# Generate strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
JWT_SECRET_KEY=your-generated-secret-key-here

# Restart backend
docker compose restart backend
```

---

### Issue: OpenAI API Key Exposed

**Problem:** API key in logs or error messages

**Solution:**
```bash
# 1. Remove API key from .env if committed to git
# 2. Add .env to .gitignore
echo ".env" >> .gitignore

# 3. Rotate API key (get new key from OpenAI dashboard)
# 4. Update .env with new key
OPENAI_API_KEY=sk-proj-new-key-here

# 5. Restart backend
docker compose restart backend
```

---

### Issue: CORS Misconfiguration

**Problem:** Allowing all origins (`*`) in production

**Solution:**
```bash
# Update .env with specific origins
# Development:
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Production:
ALLOWED_ORIGINS=https://app.yourdomain.com,https://www.yourdomain.com

# Restart backend
docker compose restart backend
```

---

### Issue: Rate Limiting Not Enforced

**Problem:** API endpoints vulnerable to abuse

**Solution:**
```python
# backend/app/api/ai.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/suggest/task")
@limiter.limit("100/60 seconds")  # 100 requests per 60 seconds
async def suggest_task(
    request: Request,
    data: SuggestionRequest,
    user_id: str = Depends(get_current_user)
):
    # ... implementation
```

---

## Monitoring and Logging

### Enable Structured Logging

```python
# backend/app/core/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitor Health Endpoints

```bash
# Create health check script
cat > health-check.sh << 'EOF'
#!/bin/bash
echo "Checking API health..."
curl -s http://localhost:8000/health | jq .

echo "Checking Socket.IO health..."
curl -s http://localhost:8000/health/socket | jq .

echo "Checking AI service health..."
curl -s http://localhost:8000/ai/health | jq .

echo "Checking MongoDB..."
docker exec -it pulsetask-mongodb-1 mongosh --eval "db.adminCommand('ping')" | grep "ok"

echo "Checking Redis..."
docker exec -it pulsetask-redis-1 redis-cli ping
EOF

chmod +x health-check.sh
./health-check.sh
```

---

## Getting Help

### Before Asking for Help

1. ✅ Check logs: `docker compose logs backend -f`
2. ✅ Verify environment: Check `.env` file
3. ✅ Test dependencies: Ensure MongoDB and Redis are running
4. ✅ Search existing issues: Check GitHub issues
5. ✅ Review documentation: Read related docs

### Report Issues With

1. **Error messages** (full stack trace)
2. **Steps to reproduce** (what you did)
3. **Expected behavior** (what should happen)
4. **Actual behavior** (what happened)
5. **Environment info**:
   ```bash
   docker --version
   python --version
   docker compose version
   cat .env | grep -v "SECRET\|KEY\|PASSWORD"  # Remove secrets!
   ```

### Support Channels

- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: `/docs` directory
- **API Reference**: `http://localhost:8000/docs` (when running)

---

**Last Updated:** 2026-03-03
**Version:** 1.0.0
