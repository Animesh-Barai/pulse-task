# Setup Guide

Complete guide for setting up the PulseTasks development environment.

---

## Quick Reference

| Step | Command | Time |
|------|---------|------|
| 1. Clone repository | `git clone repo && cd PulseTask` | 1 min |
| 2. Start databases | `docker compose up mongodb redis -d` | 2 min |
| 3. Setup Python env | `python -m venv venv && source venv/bin/activate` | 2 min |
| 4. Install dependencies | `pip install -r requirements.txt` | 3 min |
| 5. Configure environment | `cp .env.example .env` | 1 min |
| 6. Verify setup | `pytest tests/ -v` | 1 min |

**Total Time:** ~10 minutes

---

## Prerequisites

### Required Software

**System Requirements:**
- **Operating System**: Windows 10+, macOS 11+, or Linux (Ubuntu 20.04+)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 5GB minimum

**Required Tools:**

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Docker** | 20.10+ | Container management |
| **Docker Compose** | 2.0+ | Multi-container setup |
| **Git** | 2.25+ | Version control |
| **Node.js** | 18+ | Frontend (optional) |

### Verify Installation

```bash
# Check Python
python --version
# Expected: Python 3.11.x or higher

# Check Docker
docker --version
# Expected: Docker version 20.10.x

# Check Docker Compose
docker compose version
# Expected: Docker Compose version v2.x.x

# Check Git
git --version
# Expected: git version 2.25.x
```

---

## Development Environment Setup

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/pulsetask.git
cd PulseTask

# Verify repository structure
ls -la
# Expected: backend/, docs/, docker-compose.yml, etc.
```

### Step 2: Start Infrastructure Services

```bash
# Start MongoDB and Redis containers
docker compose up mongodb redis -d

# Verify containers are running
docker ps
# Expected output:
# CONTAINER ID   IMAGE          STATUS
# abc123         mongo:7.0      Up 2 minutes
# def456         redis:7-alpine Up 2 minutes

# View logs (if needed)
docker compose logs mongodb
docker compose logs redis
```

### Step 3: Setup Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python
# Expected: /path/to/PulseTask/backend/venv/bin/python
```

### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list
# Expected: FastAPI, uvicorn, motor, redis, etc.
```

### Step 5: Configure Environment Variables

```bash
# Create .env file from template
cd ..
cp .env.example .env

# Edit .env file with your settings
# Use your preferred editor: nano, vim, VS Code, etc.
code .env
```

**`.env` file example:**

```env
# Application
APP_NAME=pulsetasks
APP_ENV=development
FRONTEND_URL=http://localhost:3000

# Database
MONGODB_URL=mongodb://admin:password@localhost:27017/pulsetasks?authSource=admin
DATABASE_NAME=pulsetasks

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI (Optional)
OPENAI_API_KEY=sk-proj-your-api-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Step 6: Initialize Database

```bash
# Connect to MongoDB and create indexes
cd backend
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password

# In MongoDB shell:
use pulsetasks

# Create collections (optional - auto-created)
db.createCollection("users")
db.createCollection("tasks")
db.createCollection("ydocs")
db.createCollection("workspaces")
db.createCollection("refresh_tokens")

# Create indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.tasks.createIndex({ "list_id": 1 })
db.tasks.createIndex({ "assignee_id": 1 })
db.tasks.createIndex({ "status": 1 })
db.ydocs.createIndex({ "list_id": 1 }, { unique: true })
db.refresh_tokens.createIndex({ "token": 1 }, { unique: true })

# Exit MongoDB shell
exit
```

---

## Testing Setup

### Run All Tests

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already)
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run all tests
pytest tests/ -v

# Expected output:
# tests/unit/test_auth_service.py::TestAuthService::test_register_user_success PASSED
# ...
# ==== XX passed, YY failed in Z.ZZs ====
```

### Run Specific Test Suite

```bash
# Run unit tests only
pytest tests/unit/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_auth_service.py -v

# Run specific test
pytest tests/unit/test_auth_service.py::TestAuthService::test_register_user_success -v
```

### Run Tests with Coverage

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux

# Expected coverage: > 80%
```

### Test Configuration

**`pytest.ini` (if needed):**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html
asyncio_mode = auto
```

---

## VS Code Configuration

### Recommended Extensions

Install these extensions for optimal development experience:

1. **Python** - Microsoft (Python language support)
2. **Pylance** - Microsoft (Fast IntelliSense)
3. **Python Test Explorer** - LittleFoxTeam (Test integration)
4. **Docker** - Microsoft (Docker support)
5. **GitLens** - GitKraken (Git supercharged)
6. **ESLint** - Microsoft (JavaScript linting)
7. **Prettier** - Prettier (Code formatting)

### VS Code Settings

**`.vscode/settings.json`:**

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/venv": true,
    "**/*.pyc": true
  },
  "files.watcherExclude": {
    "**/__pycache__/**": true,
    "**/.pytest_cache/**": true,
    "**/venv/**": true
  }
}
```

### VS Code Extensions for Debugging

**`.vscode/launch.json`:**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/.env",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Python: Pytest",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": [
        "-v",
        "--tb=short",
        "tests/"
      ],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal"
    }
  ]
}
```

---

## Running the Application

### Development Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start FastAPI server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### Verify Application is Running

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "pulsetasks-backend",
#   "socketio": "running"
# }

# Access API documentation
# Open in browser: http://localhost:8000/docs
```

### Accessing API Documentation

1. **Swagger UI**: http://localhost:8000/docs
   - Interactive API explorer
   - Test endpoints directly

2. **ReDoc**: http://localhost:8000/redoc
   - Alternative documentation viewer

3. **OpenAPI Spec**: http://localhost:8000/openapi.json
   - Raw OpenAPI specification

---

## Common Development Workflows

### Running Tests While Coding

```bash
# Watch mode - re-run tests on file changes
pytest-watch  # Requires: pip install pytest-watch

# Or manually re-run specific test
pytest tests/unit/test_auth_service.py::TestAuthService::test_register_user_success -v
```

### Debugging with Print Statements

```python
# Add debug prints
print(f"DEBUG: user_data = {user_data}")
print(f"DEBUG: query result = {result}")

# Run with output
pytest tests/ -v -s  # -s shows print output
```

### Checking Database State

```bash
# Connect to MongoDB
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password

# List all collections
use pulsetasks
show collections

# Query users
db.users.find().pretty()

# Query tasks
db.tasks.find().pretty()

# Count documents
db.users.countDocuments()
db.tasks.countDocuments()

# Exit
exit
```

### Checking Redis State

```bash
# Connect to Redis
docker exec -it pulsetask-redis-1 redis-cli

# Check all keys
KEYS *

# Check specific key
GET cache:ai:suggestion:abc123

# Check presence data
HGETALL presence:workspace:ws_abc123

# Flush all data (development only)
FLUSHALL

# Exit
exit
```

---

## Troubleshooting

### Issue: Python Version Too Old

**Problem:** `python --version` shows Python 3.9 or earlier

**Solution:**
```bash
# Install Python 3.11+ from python.org
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu:
sudo apt update
sudo apt install python3.11 python3.11-venv

# On Windows:
# Download from https://www.python.org/downloads/
```

### Issue: Docker Permission Denied

**Problem:** `docker: Got permission denied`

**Solution:**
```bash
# Add user to docker group (Linux/macOS)
sudo usermod -aG docker $USER

# Log out and log back in
# Or run with sudo (not recommended)
sudo docker ps
```

### Issue: Port Already in Use

**Problem:** `Error: Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: MongoDB Connection Failed

**Problem:** `pymongo.errors.ConnectionFailure`

**Solution:**
```bash
# Check MongoDB container status
docker ps | grep mongo

# Check MongoDB logs
docker compose logs mongodb

# Restart MongoDB
docker compose restart mongodb

# Verify connection string in .env
# MONGODB_URL=mongodb://admin:password@localhost:27017/pulsetasks?authSource=admin
```

### Issue: Redis Connection Failed

**Problem:** `redis.exceptions.ConnectionError`

**Solution:**
```bash
# Check Redis container status
docker ps | grep redis

# Check Redis logs
docker compose logs redis

# Restart Redis
docker compose restart redis

# Test connection
docker exec -it pulsetask-redis-1 redis-cli ping
# Expected: PONG
```

### Issue: Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Ensure you're in backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Issue: Tests Failing

**Problem:** Tests fail with database errors

**Solution:**
```bash
# Ensure databases are running
docker compose ps

# Rebuild test database
docker compose down -v
docker compose up mongodb redis -d

# Run tests with verbose output
pytest tests/ -vv --tb=long

# Check test logs
pytest tests/ --log-cli-level=DEBUG
```

---

## Code Quality Tools

### Linting with Flake8

```bash
# Run flake8
flake8 backend/app

# Fix common issues automatically
black backend/app/
isort backend/app/

# Run all checks
flake8 backend/app && mypy backend/app && pytest tests/
```

### Type Checking with mypy

```bash
# Run mypy
mypy backend/app

# Fix type errors
# Edit code to add type hints as suggested
```

### Formatting with Black

```bash
# Format all Python files
black backend/app/

# Check if formatting is needed
black --check backend/app/

# Format specific file
black backend/app/main.py
```

---

## Useful Commands

### Docker Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (reset database)
docker compose down -v

# View logs
docker compose logs -f

# Restart service
docker compose restart mongodb

# Execute command in container
docker exec -it pulsetask-mongodb-1 bash
```

### Python Commands

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Deactivate virtual environment
deactivate

# Install package
pip install package-name

# Install from requirements
pip install -r requirements.txt

# Freeze dependencies
pip freeze > requirements.txt
```

### Git Commands

```bash
# Check status
git status

# Add files
git add .

# Commit
git commit -m "Add feature"

# Pull changes
git pull origin main

# Push changes
git push origin main

# View branches
git branch -a
```

---

## Next Steps

After completing the setup:

1. ✅ Read the [API Documentation](API_DOCUMENTATION.md) to understand available endpoints
2. ✅ Review the [Architecture](ARCHITECTURE.md) to understand system design
3. ✅ Check the [Deployment Guide](DEPLOYMENT_GUIDE.md) for production deployment
4. ✅ Explore the codebase starting with `backend/app/main.py`
5. ✅ Run existing tests to verify setup: `pytest tests/ -v`

---

**Need Help?**
- Check the [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues
- Review the [Quick Start Guide](QUICK_START_GUIDE.md) for TDD workflow
- Open an issue on GitHub with detailed error messages

---

**Last Updated:** 2026-03-03
**Version:** 1.0.0
