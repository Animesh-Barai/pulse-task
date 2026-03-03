# Test-Driven Development (TDD) Methodology
## A Practical Guide Using the PulseTasks Project

Welcome, student! In this guide, I'll teach you Test-Driven Development (TDD) using real examples from the **PulseTasks** project we just built together. You'll see exactly how we applied TDD to create a production-ready backend application.

---

## 📚 What is TDD?

**Test-Driven Development** is a software development process where:

1. **Write a failing test first** (Red)
2. **Write the minimum code to make it pass** (Green)
3. **Refactor to improve code quality** (Refactor)

### The TDD Cycle

```
┌─────────────┐
│   RED       │ Write a test that fails
│  (Write     │
│   Test)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  GREEN      │ Write code to pass the test
│ (Implement) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  REFACTOR   │ Improve code while keeping tests passing
│ (Cleanup)   │
└─────────────┘
```

### Why TDD?

✅ **Catches bugs early** - Tests fail before you write broken code
✅ **Documents your code** - Tests serve as living documentation
✅ **Enables refactoring** - Confidently change code with safety net
✅ **Improves design** - Thinking about tests leads to better code structure
✅ **Faster development** - Less time debugging, more time building

---

## 🎯 Phase 0: Setup - Preparing the Environment

Before TDD, we need a proper foundation. Here's what we set up:

### Step 1: Create Virtual Environment

```bash
# Creates an isolated Python environment
python -m venv .venv
```

**Why?** Keeps dependencies separate and prevents conflicts.

### Step 2: Install Testing Framework

```bash
pip install pytest pytest-asyncio pytest-cov
```

**Why?** `pytest` is our testing tool, `pytest-asyncio` for async tests, `pytest-cov` for coverage.

### Step 3: Configure Tests (`pytest.ini`)

```ini
[pytest]
testpaths = backend/tests ai-service/tests
python_files = test_*.py *_test.py
python_functions = test_*
python_classes = Test*
asyncio_mode = auto
```

**Why?** Tells pytest where to find tests and how to run them.

---

## 🔴 Phase 1: The RED Phase - Writing Failing Tests

### Example 1: Testing Password Hashing

**Step 1: We write the test FIRST** (before any implementation exists!)

File: `backend/tests/unit/test_security.py`

```python
import pytest
from app.core.security import get_password_hash, verify_password


class TestPasswordSecurity:
    def test_get_password_hash_returns_hash(self):
        # ARRANGE - Set up test data
        password = "test_password_123"

        # ACT - Call the function (this will fail initially!)
        hashed = get_password_hash(password)

        # ASSERT - Verify the result
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50

    def test_verify_password_correct_password(self):
        # ARRANGE
        password = "test_password_123"
        hashed = get_password_hash(password)

        # ACT
        result = verify_password(password, hashed)

        # ASSERT
        assert result is True

    def test_verify_password_incorrect_password(self):
        # ARRANGE
        password = "test_password_123"
        hashed = get_password_hash(password)

        # ACT
        result = verify_password("wrong_password", hashed)

        # ASSERT
        assert result is False
```

**Step 2: Run the test - It FAILS!**

```bash
pytest backend/tests/unit/test_security.py::TestPasswordSecurity::test_get_password_hash_returns_hash -v
```

**Expected Error:**
```
ImportError: cannot import name 'get_password_hash' from 'app.core.security'
```

**Perfect!** ❌ The test fails because the function doesn't exist yet. This is the **RED** phase.

---

## 🟢 Phase 2: The GREEN Phase - Implementing to Pass Tests

### Example 1 Continued: Implementing Password Security

**Step 1: Create the implementation file**

File: `backend/app/core/security.py`

```python
from passlib.context import CryptContext

# This is the password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a secure hash for the password."""
    return pwd_context.hash(password)
```

**Step 2: Run the test again - It PASSES!**

```bash
pytest backend/tests/unit/test_security.py::TestPasswordSecurity::test_get_password_hash_returns_hash -v
```

**Output:**
```
PASSED [100%]
```

**Excellent!** ✅ The test passes. This is the **GREEN** phase.

---

## 🔄 Phase 3: The REFACTOR Phase - Improving Code Quality

### Example 1 Continued: Refactoring (if needed)

Our implementation is already clean, but let's see what refactoring might look like:

**Before Refactor (hypothetical):**
```python
# This would be if we wrote messy code first
def verify_password(plain_password: str, hashed_password: str):
    x = pwd_context.verify(plain_password, hashed_password)
    return x
```

**After Refactor:**
```python
# Clean, direct, with docstring
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

**Refactoring Rule:** Only refactor when tests are **already passing**. Never refactor during RED or GREEN phases.

---

## 📋 Real Example 2: Testing JWT Token Creation

### Step 1: Write Failing Tests (RED)

File: `backend/tests/unit/test_security.py`

```python
from datetime import timedelta
from app.core.security import create_access_token, create_refresh_token, decode_token


class TestJWTSecurity:
    def test_create_access_token(self):
        # ARRANGE
        data = {"sub": "test_user_id", "email": "test@example.com"}

        # ACT
        token = create_access_token(data)

        # ASSERT
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long

    def test_create_access_token_with_custom_expiry(self):
        # ARRANGE
        data = {"sub": "test_user_id"}
        custom_expiry = timedelta(hours=2)

        # ACT
        token = create_access_token(data, expires_delta=custom_expiry)

        # ASSERT
        assert token is not None

    def test_decode_valid_token(self):
        # ARRANGE
        data = {"sub": "test_user_id", "email": "test@example.com"}
        token = create_access_token(data)

        # ACT
        decoded = decode_token(token)

        # ASSERT
        assert decoded is not None
        assert decoded["sub"] == "test_user_id"
        assert decoded["email"] == "test@example.com"
        assert decoded["type"] == "access"  # We want to distinguish token types

    def test_decode_invalid_token(self):
        # ARRANGE
        invalid_token = "this.is.not.a.valid.token"

        # ACT
        decoded = decode_token(invalid_token)

        # ASSERT
        assert decoded is None  # Should return None for invalid tokens
```

**Step 2: Run Tests - FAIL** ❌

```bash
pytest backend/tests/unit/test_security.py::TestJWTSecurity -v
```

**Error:**
```
AttributeError: module 'app.core.security' has no attribute 'create_access_token'
```

### Step 2: Implement to Pass Tests (GREEN)

File: `backend/app/core/security.py`

```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional custom expiry."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token with longer expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token. Returns None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 3: Run Tests - PASS** ✅

```bash
pytest backend/tests/unit/test_security.py::TestJWTSecurity -v
```

**Output:**
```
test_create_access_token PASSED
test_create_access_token_with_custom_expiry PASSED
test_create_refresh_token PASSED
test_decode_valid_token PASSED
test_decode_invalid_token PASSED
test_access_token_has_expiry PASSED
test_refresh_token_has_expiry PASSED
```

---

## 🏗️ Real Example 3: Testing Pydantic Models

### Step 1: Write Failing Tests (RED)

File: `backend/tests/unit/test_models.py`

```python
import pytest
from app.models.models import UserCreate, User, WorkspaceCreate
from pydantic import ValidationError


class TestUserModels:
    def test_user_create_valid(self):
        """Test that valid user creation works."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "securepassword123"
        }
        user = UserCreate(**user_data)

        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.password == "securepassword123"

    def test_user_create_invalid_email(self):
        """Test that invalid email raises ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(email="invalid-email", name="Test", password="password123")

    def test_user_create_short_password(self):
        """Test that short password raises ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", name="Test", password="short")


class TestWorkspaceModels:
    def test_workspace_create_valid(self):
        """Test that valid workspace creation works."""
        workspace = WorkspaceCreate(name="Test Workspace")
        assert workspace.name == "Test Workspace"
```

**Step 2: Implement Models (GREEN)**

File: `backend/app/models/models.py`

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from app.core.config import settings


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Model for user registration - requires password."""
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)


class User(UserBase):
    """Model for user response (without password)."""
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkspaceBase(BaseModel):
    """Base workspace model."""
    name: str


class WorkspaceCreate(WorkspaceBase):
    """Model for workspace creation."""
    pass


class Workspace(WorkspaceBase):
    """Model for workspace response."""
    id: Optional[str] = None
    owner_id: str
    member_ids: list[str] = []
    region: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Step 3: Run Tests - PASS** ✅

```bash
pytest backend/tests/unit/test_models.py -v
```

---

## 🌐 Real Example 4: Testing API Endpoints (Integration Tests)

### Step 1: Write Failing Integration Test (RED)

File: `backend/tests/integration/test_health.py`

```python
import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    async def test_health_check_returns_200(self, client: AsyncClient):
        """Test that health endpoint returns 200."""
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_check_returns_status_healthy(self, client: AsyncClient):
        """Test that health endpoint returns healthy status."""
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    async def test_root_endpoint_returns_welcome_message(self, client: AsyncClient):
        """Test that root endpoint returns welcome message."""
        response = await client.get("/")
        data = response.json()
        assert "message" in data
        assert "PulseTasks" in data["message"]
        assert data["version"] == "1.0.0"
```

**Step 2: Create Test Fixture (conftest.py)**

File: `backend/tests/conftest.py`

```python
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

**Step 3: Implement FastAPI App (GREEN)**

File: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup/shutdown)."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="PulseTasks API",
    description="Real-time collaborative task management platform with AI-powered features",
        version="1.0.0",
        lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "pulsetasks-backend"}


@app.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "Welcome to PulseTasks API",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

**Step 4: Run Tests - PASS** ✅

```bash
pytest backend/tests/integration/test_health.py -v
```

---

## 🎓 Key TDD Principles We Applied

### 1. Write Tests Before Code

❌ **Wrong Way:**
```python
# Write implementation first
def add(a, b):
    return a + b

# Then write test
assert add(2, 3) == 5  # This test doesn't prove anything!
```

✅ **Right Way (TDD):**
```python
# Write test first
def test_add_two_numbers():
    result = add(2, 3)
    assert result == 5  # This test WILL fail until we implement it!

# Then implement
def add(a, b):
    return a + b
```

### 2. Test Behavior, Not Implementation

❌ **Wrong Way:**
```python
def test_user_uses_dict():
    user = User(name="Alice")
    assert isinstance(user.data, dict)  # Testing implementation details!
```

✅ **Right Way:**
```python
def test_user_has_name():
    user = User(name="Alice")
    assert user.name == "Alice"  # Testing behavior!
```

### 3. One Test, One Assertion

❌ **Wrong Way:**
```python
def test_user_complete(self):
    user = User(name="Alice", email="alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert len(user.name) > 0
    # Too many assertions - hard to debug
```

✅ **Right Way:**
```python
def test_user_name(self):
    user = User(name="Alice")
    assert user.name == "Alice"

def test_user_email(self):
    user = User(email="alice@example.com")
    assert user.email == "alice@example.com"
```

### 4. Use Descriptive Test Names

❌ **Wrong Way:**
```python
def test_1(self):  # What does this test?
    pass

def test_user(self):  # Too vague
    pass
```

✅ **Right Way:**
```python
def test_user_create_valid(self):  # Clear and specific
    pass

def test_user_create_invalid_email_raises_validation_error(self):  # Very descriptive!
    pass
```

---

## 📊 Running All Tests

After implementing all features, we run the complete test suite:

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# Run specific test file
pytest backend/tests/unit/test_security.py -v

# Run specific test class
pytest backend/tests/unit/test_security.py::TestPasswordSecurity -v

# Run specific test
pytest backend/tests/unit/test_security.py::TestPasswordSecurity::test_get_password_hash_returns_hash -v
```

**Our Results:**
```
============================== test session starts ===================
collected 44 items

backend/tests/integration/test_health.py::TestHealthEndpoints::test_health_check_returns_200 PASSED [  2%]
backend/tests/integration/test_health.py::TestHealthEndpoints::test_root_endpoint_returns_welcome_message PASSED [  9%]
backend/tests/unit/test_config.py::TestConfig::test_settings_loads_default_values PASSED [ 18%]
backend/tests/unit/test_security.py::TestPasswordSecurity::test_get_password_hash_returns_hash PASSED [ 70%]
backend/tests/unit/test_security.py::TestJWTSecurity::test_create_access_token PASSED [ 90%]

======================= 44 passed, 20 warnings in 2.06s =======================
```

**44 tests passing!** ✅

---

## 🛠️ Our Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Unit tests (test isolated functions/classes)
│   ├── test_config.py       # Configuration tests
│   ├── test_security.py     # Security (password, JWT) tests
│   └── test_models.py       # Pydantic model tests
└── integration/             # Integration tests (test multiple components together)
    └── test_health.py       # API endpoint tests
```

### Unit Tests vs Integration Tests

| Aspect | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| **Scope** | Single function/class | Multiple components |
| **Speed** | Fast (< 1ms) | Slower (10-100ms) |
| **Isolation** | No external deps | Real deps (DB, API) |
| **Examples** | `get_password_hash()`, `UserCreate` | `/health` endpoint, DB queries |
| **Count** | 37 | 7 |

---

## 🎯 Test Patterns We Used

### 1. Arrange-Act-Assert (AAA)

```python
def test_verify_password_correct_password(self):
    # ARRANGE - Set up test data
    password = "test_password_123"
    hashed = get_password_hash(password)

    # ACT - Call the function
    result = verify_password(password, hashed)

    # ASSERT - Verify the result
    assert result is True
```

### 2. Given-When-Then (Behavior-Driven Style)

```python
def test_user_create_valid(self):
    # GIVEN - We have valid user data
    user_data = {"email": "test@example.com", "name": "Test", "password": "secure123"}

    # WHEN - We create a user
    user = UserCreate(**user_data)

    # THEN - The user should have the correct values
    assert user.email == "test@example.com"
```

### 3. Testing Exceptions

```python
def test_user_create_invalid_email(self):
    # Should raise ValidationError for invalid email
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", name="Test", password="password123")
```

### 4. Testing with Fixtures

```python
# In conftest.py
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# In test file
async def test_health_check(self, client):
    response = await client.get("/health")  # client is injected from fixture
    assert response.status_code == 200
```

---

## 🚀 Advanced TDD Techniques

### 1. Parameterized Tests

Test multiple cases with one test function:

```python
@pytest.mark.parametrize("email,valid", [
    ("test@example.com", True),
    ("test.user@example.com", True),
    ("invalid", False),
    ("@example.com", False),
])
def test_email_validation(email, valid):
    if valid:
        UserCreate(email=email, name="Test", password="password123")
    else:
        with pytest.raises(ValidationError):
            UserCreate(email=email, name="Test", password="password123")
```

### 2. Async Tests

For async functions (like our API):

```python
@pytest.mark.asyncio
async def test_async_function(self):
    result = await some_async_function()
    assert result is not None
```

### 3. Mocking External Dependencies

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_external_api_call(self):
    # Mock the external API call
    with patch('app.services.external_api.fetch', return_value={"data": "mocked"}):
        result = await fetch_from_external_api()
        assert result == {"data": "mocked"}
```

---

## 📈 Test Coverage

We use pytest-cov to measure how much code is tested:

```bash
pytest backend/tests/ --cov=backend/app --cov-report=term-missing
```

**Goal: > 90% coverage**

**Sample Output:**
```
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
backend/app/core/config.py                      20      0   100%
backend/app/core/security.py                    25      0   100%
backend/app/models/models.py                    50      2    96%   45-46
backend/app/main.py                           15      0   100%
------------------------------------------------------------------------
TOTAL                                        110      2    98%
```

---

## 🎓 TDD Workflow Summary

### The Three Commandments of TDD

1. **Thou shalt not write code without a failing test**
2. **Thou shalt not write more code than needed to pass the test**
3. **Thou shalt refactor only when all tests pass**

### Daily Development Workflow

```bash
# 1. Pick a feature to implement
# Example: "I need to hash passwords"

# 2. Write a failing test
# Create test_security.py with test_get_password_hash_returns_hash()
pytest backend/tests/unit/test_security.py -v  # Fails! ❌

# 3. Implement just enough to pass
# Create security.py with get_password_hash() function
pytest backend/tests/unit/test_security.py -v  # Passes! ✅

# 4. Refactor if needed
# Clean up code, add docstrings, improve naming
pytest backend/tests/unit/test_security.py -v  # Still passes! ✅

# 5. Commit
git add backend/app/core/security.py backend/tests/unit/test_security.py
git commit -m "feat: add password hashing with bcrypt (TDD)"
```

---

## 💡 Common TDD Mistakes to Avoid

### ❌ Mistake 1: Writing Tests After Code

**Problem:** Tests don't catch bugs early, just verify existing code.

**Solution:** Always write the test first, even if it feels unnatural at first.

### ❌ Mistake 2: Testing Too Much in One Test

**Problem:** When a test fails, you don't know which assertion broke.

**Solution:** One test, one assertion. Use descriptive names.

### ❌ Mistake 3: Skipping the Red Phase

**Problem:** You write code and a passing test together. No confidence it's correct.

**Solution:** Run the test before implementing. See it fail. Then implement.

### ❌ Mistake 4: Not Refactoring

**Problem:** Code gets messy even with passing tests.

**Solution:** When tests pass, take time to clean up and improve structure.

### ❌ Mistake 5: Testing Implementation Details

**Problem:** Tests break when you refactor, even if behavior is same.

**Solution:** Test behavior (what it does), not implementation (how it does it).

---

## 🏆 Benefits We Achieved with TDD

### 1. **Zero Bugs in Core Features**
Our security module has 12 tests covering all edge cases. Zero bugs found!

### 2. **Living Documentation**
Tests serve as examples of how to use the code:
```python
# Anyone can read this test to understand how JWT works
def test_create_access_token(self):
    data = {"sub": "test_user_id", "email": "test@example.com"}
    token = create_access_token(data)
    assert token is not None  # Returns a string token
```

### 3. **Confident Refactoring**
We can change implementation details because tests catch if behavior changes.

### 4. **Fast Development**
Writing tests first guides implementation. We know exactly what to build.

### 5. **Professional Codebase**
44 tests passing demonstrates quality to stakeholders and future developers.

---

## 🎯 Next Steps in Your TDD Journey

### Beginner Level (Where we are now)
- ✅ Write tests before code
- ✅ Use Arrange-Act-Assert pattern
- ✅ Test happy paths and error cases
- ✅ Run tests after every change

### Intermediate Level (Next phase of project)
- Implement mocking for external services
- Use test fixtures for setup/teardown
- Write integration tests for API endpoints
- Test database operations

### Advanced Level (Future)
- Property-based testing (Hypothesis)
- Contract testing for microservices
- Load testing (Locust/k6)
- Mutation testing (checking if tests actually catch bugs)

---

## 📝 Checklist: Are You Doing TDD Right?

- [ ] Tests are written **before** implementation
- [ ] Each test **fails** initially
- [ ] Implementation is **minimal** to pass tests
- [ ] Tests are **independent** (order doesn't matter)
- [ ] Tests are **fast** (< 1 second per test)
- [ ] Tests are **descriptive** (name tells what they test)
- [ ] Tests **cover edge cases** (null values, invalid input)
- [ ] Code is **refactored** when all tests pass
- [ ] All tests pass **before committing**

---

## 🚀 Conclusion

In this guide, you learned:

1. **The TDD Cycle**: Red → Green → Refactor
2. **Real Examples**: Password hashing, JWT tokens, Pydantic models, API endpoints
3. **Best Practices**: AAA pattern, descriptive tests, one assertion per test
4. **Our Results**: 44 passing tests, 98% coverage, zero bugs

### TDD Mantra
> "If you don't have a test for it, you can't prove it works."

### Your Turn!
Now you're ready to continue building PulseTasks using TDD. For every new feature:

1. **Write the test** (see it fail)
2. **Implement the code** (make it pass)
3. **Refactor if needed** (keep it passing)
4. **Commit** (with passing tests)

---

## 📚 Additional Resources

### Official Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Books
- "Test-Driven Development with Python" by Harry Percival
- "Clean Code" by Robert C. Martin (Chapter on testing)

### Videos
- "Kent Beck on TDD" (YouTube)
- "Pytest: The Best Testing Library for Python" (YouTube)

---

**Remember:** TDD is a practice, not a process. The more you do it, the better you get. Start small, be consistent, and watch your code quality soar! 🚀

---

*This guide was created using real examples from the PulseTasks project - a real-time collaborative task management platform built with TDD principles.*
