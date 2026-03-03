# Phase 1 TDD Execution Plan - Dual Agent Strategy

**Status**: 🟡 Ready to Execute
**Methodology**: Test-Driven Development (TDD)
**Approach**: Independent Dual-Agent Collaboration
**Duration**: 3-4 weeks (24-40 hours)

---

## 🎯 Executive Summary

This plan implements Phase 1 (Critical Backend) using strict Test-Driven Development with two independent agents working in the **Red-Green-Refactor** cycle:

### Agent Roles

**Agent A (Test Specialist)** - "The Specifier"
- Writes comprehensive test files
- Identifies all edge cases upfront
- Documents test scenarios
- Creates test fixtures and mocks
- Validates test completeness

**Agent B (Implementation Specialist)** - "The Builder"
- Reads test files only
- Implements code to pass tests
- No knowledge of test author's thinking
- Follows test specifications strictly
- Refactors code after green

### Independence Protocol

**Rule #1**: Code Agent NEVER sees Test Agent's thinking process
**Rule #2**: Communication happens ONLY through test files
**Rule #3**: Code Agent implements exactly what tests specify
**Rule #4**: Tests must pass 100% before moving to next task
**Rule #5**: Refactoring happens only after all tests pass

---

## 📋 Phase 1 Task Breakdown for TDD

| # | Task | Test Cases | Implementation | Estimated Time |
|---|------|-------------|----------------|-----------------|
| 1.1 | Fix unit tests | 17 failing tests | 17 fixes | 3-5 hours |
| 1.2 | Socket.IO server | 15 test suites | Server + events | 8-12 hours |
| 1.3 | AI service MVP | 12 test suites | Service + OpenAI | 8-12 hours |
| 1.4 | Celery workers | 8 test suites | Workers + tasks | 4-8 hours |

**Total TDD Cycles**: 52 cycles
**Total Estimated Time**: 23-37 hours

---

## 🔄 TDD Cycle Protocol

### The Red-Green-Refactor Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    TDD CYCLE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: RED (Test Agent)                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Analyze task requirements                   │    │
│  │ 2. Identify ALL edge cases                      │    │
│  │ 3. Write failing tests (RED state)            │    │
│  │ 4. Document test scenarios                     │    │
│  │ 5. Validate test completeness                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                         ↓                                     │
│  STEP 2: GREEN (Code Agent)                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Read test file (NO thinking process)       │    │
│  │ 2. Implement minimal code to pass tests       │    │
│  │ 3. Run tests (GREEN state)                   │    │
│  │ 4. Verify 100% pass rate                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                         ↓                                     │
│  STEP 3: REFACTOR (Code Agent)                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Review code quality                         │    │
│  │ 2. Improve design while tests stay green     │    │
│  │ 3. Add documentation                       │    │
│  │ 4. Verify tests still pass (GREEN)          │    │
│  └─────────────────────────────────────────────────────┘    │
│                         ↓                                     │
│  STEP 4: VALIDATE (Test Agent)                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Run all tests                              │    │
│  │ 2. Verify test coverage > 80%              │    │
│  │ 3. Check for edge cases missed               │    │
│  │ 4. Document results                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                         ↓                                     │
│              NEXT TASK / NEXT TDD CYCLE                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Task 1.1: Fix Failing Unit Tests

### Objective
Get all 39 unit tests passing (currently 22/39 passing)

### Test Agent Responsibilities

#### 1.1.1 Analyze Failing Tests

**Action**: Read and analyze all failing test files

**Files to Analyze**:
```
backend/tests/unit/test_auth_service.py    # 17 failing
backend/tests/unit/test_task_service.py    # 13 failing
backend/tests/unit/test_crdt_service.py    # 10 failing
```

**Analysis Checklist**:
- [ ] Identify root cause of each failure
- [ ] Categorize failures (async, mock, fixture, etc.)
- [ ] Document expected vs actual behavior
- [ ] List missing dependencies

#### 1.1.2 Rewrite Test Files with All Edge Cases

**File**: `backend/tests/unit/test_auth_service.py`

**Test Cases to Write** (Must include ALL):

```python
# Test 1: User Registration - Happy Path
- Valid email and password
- Password meets minimum length
- User does not already exist
- Returns success with tokens
- Tokens have correct structure

# Test 2: User Registration - Edge Cases
- Email already exists (duplicate)
- Password too short (<8 chars)
- Email invalid format
- Empty fields
- Password with only numbers
- Password with only letters
- Password with special chars
- Password exceeds max length
- Email with trailing spaces
- Email in mixed case

# Test 3: User Login - Happy Path
- Valid credentials
- Returns access and refresh tokens
- Token has correct expiration

# Test 4: User Login - Edge Cases
- Wrong password
- Non-existent user
- Empty credentials
- Wrong email format
- Case-sensitive email check
- Account disabled (if applicable)
- Too many login attempts (rate limit)
- Expired refresh token

# Test 5: Token Refresh - Happy Path
- Valid refresh token
- Returns new access token
- Preserves user identity

# Test 6: Token Refresh - Edge Cases
- Invalid refresh token
- Expired refresh token
- Tampered refresh token
- Refresh token already used
- No refresh token provided
- Revoked refresh token
- Refresh token for deleted user

# Test 7: Password Hashing - Happy Path
- Hash password correctly
- Different hashes for same password (with salt)
- Verify password matches hash

# Test 8: Password Hashing - Edge Cases
- Empty password
- Very long password (>100 chars)
- Password with null bytes
- Password with unicode characters
- Password with emoji
- Password with whitespace only
- Password with leading/trailing spaces

# Test 9: Token Generation - Happy Path
- Generate access token
- Generate refresh token
- Tokens are JWT format
- Tokens have correct claims

# Test 10: Token Generation - Edge Cases
- Token with no expiration
- Token with custom claims
- Token with very long claims
- Token with invalid claims
- Token with missing claims
- Token with extra claims
```

**Test File Structure**:
```python
# backend/tests/unit/test_auth_service.py

import pytest
from backend.app.services.auth_service import AuthService
from backend.app.core.security import hash_password, verify_password
from datetime import datetime, timedelta

class TestAuthService:
    """Auth Service - User Registration"""

    async def test_register_user_success(self):
        """Test: Register user with valid credentials"""
        # Given
        email = "test@example.com"
        password = "SecurePass123"
        name = "Test User"

        # When
        result = await auth_service.register(email, password, name)

        # Then
        assert result["success"] is True
        assert "user" in result
        assert result["user"]["email"] == email
        assert "tokens" in result
        assert "access_token" in result["tokens"]
        assert "refresh_token" in result["tokens"]

    async def test_register_user_duplicate_email(self):
        """Test: Register with duplicate email"""
        # Given
        email = "test@example.com"
        password = "SecurePass123"
        name = "Test User"

        # When: Register first user
        await auth_service.register(email, password, name)

        # Then: Register same email again
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register(email, password, name)

    async def test_register_user_password_too_short(self):
        """Test: Register with password too short"""
        # Given
        email = "test@example.com"
        password = "Short1"  # < 8 chars

        # When/Then
        with pytest.raises(ValueError, match="Password too short"):
            await auth_service.register(email, password, "Test")

    async def test_register_user_invalid_email_format(self):
        """Test: Register with invalid email format"""
        # Given
        email = "invalid-email"
        password = "SecurePass123"

        # When/Then
        with pytest.raises(ValueError, match="Invalid email format"):
            await auth_service.register(email, password, "Test")

    async def test_register_user_empty_fields(self):
        """Test: Register with empty fields"""
        # When/Then
        with pytest.raises(ValueError):
            await auth_service.register("", "", "")

    async def test_register_user_password_numbers_only(self):
        """Test: Register with password containing only numbers"""
        # Given
        email = "test@example.com"
        password = "12345678"

        # When
        result = await auth_service.register(email, password, "Test")

        # Then: Should succeed but maybe warn
        assert result["success"] is True

    async def test_register_user_password_letters_only(self):
        """Test: Register with password containing only letters"""
        # Given
        email = "test@example.com"
        password = "abcdefgh"

        # When
        result = await auth_service.register(email, password, "Test")

        # Then
        assert result["success"] is True

    async def test_register_user_password_special_chars(self):
        """Test: Register with password containing special chars"""
        # Given
        email = "test@example.com"
        password = "P@$$w0rd!23"

        # When
        result = await auth_service.register(email, password, "Test")

        # Then
        assert result["success"] is True

    async def test_register_user_password_too_long(self):
        """Test: Register with password exceeding max length"""
        # Given
        email = "test@example.com"
        password = "a" * 101  # > 100 chars

        # When/Then
        with pytest.raises(ValueError, match="Password too long"):
            await auth_service.register(email, password, "Test")

    async def test_register_user_email_trailing_spaces(self):
        """Test: Register with email having trailing spaces"""
        # Given
        email = "  test@example.com  "
        password = "SecurePass123"

        # When/Then
        with pytest.raises(ValueError, match="Invalid email format"):
            await auth_service.register(email, password, "Test")

    async def test_register_user_email_mixed_case(self):
        """Test: Register with email in mixed case"""
        # Given
        email = "Test@Example.COM"
        password = "SecurePass123"

        # When
        result = await auth_service.register(email, password, "Test")

        # Then: Should normalize to lowercase
        assert result["user"]["email"] == email.lower()

class TestAuthServiceLogin:
    """Auth Service - User Login"""

    async def test_login_user_success(self):
        """Test: Login with valid credentials"""
        # Given
        email = "test@example.com"
        password = "SecurePass123"

        # When
        result = await auth_service.login(email, password)

        # Then
        assert result["success"] is True
        assert "user" in result
        assert "tokens" in result

    async def test_login_user_wrong_password(self):
        """Test: Login with wrong password"""
        # When/Then
        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.login("test@example.com", "WrongPass")

    async def test_login_user_nonexistent(self):
        """Test: Login with non-existent user"""
        # When/Then
        with pytest.raises(ValueError, match="User not found"):
            await auth_service.login("nonexistent@example.com", "password")

    async def test_login_user_empty_credentials(self):
        """Test: Login with empty credentials"""
        # When/Then
        with pytest.raises(ValueError):
            await auth_service.login("", "")

    async def test_login_user_wrong_email_format(self):
        """Test: Login with invalid email format"""
        # When/Then
        with pytest.raises(ValueError, match="Invalid email format"):
            await auth_service.login("invalid-email", "password")

    async def test_login_user_case_sensitive_email(self):
        """Test: Login with email in different case"""
        # Given
        await auth_service.register("test@example.com", "pass123", "Test")

        # When: Try login with different case
        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.login("TEST@EXAMPLE.COM", "pass123")

    async def test_login_user_too_many_attempts(self):
        """Test: Login with too many attempts (rate limiting)"""
        # Given
        email = "test@example.com"
        password = "SecurePass123"

        # When: Try login 6 times with wrong password
        for i in range(6):
            try:
                await auth_service.login(email, "wrong")
            except ValueError:
                pass

        # Then: 6th attempt should be rate-limited
        with pytest.raises(ValueError, match="Too many attempts"):
            await auth_service.login(email, password)

class TestAuthServiceTokenRefresh:
    """Auth Service - Token Refresh"""

    async def test_refresh_token_valid(self):
        """Test: Refresh with valid token"""
        # Given
        user = await auth_service.register("test@example.com", "pass", "Test")
        refresh_token = user["tokens"]["refresh_token"]

        # When
        result = await auth_service.refresh_token(refresh_token)

        # Then
        assert result["success"] is True
        assert "access_token" in result
        assert "refresh_token" in result

    async def test_refresh_token_invalid(self):
        """Test: Refresh with invalid token"""
        # When/Then
        with pytest.raises(ValueError, match="Invalid refresh token"):
            await auth_service.refresh_token("invalid_token")

    async def test_refresh_token_expired(self):
        """Test: Refresh with expired token"""
        # Given: Create expired token
        expired_token = create_expired_token()

        # When/Then
        with pytest.raises(ValueError, match="Expired refresh token"):
            await auth_service.refresh_token(expired_token)

    async def test_refresh_token_tampered(self):
        """Test: Refresh with tampered token"""
        # Given: Tamper token
        valid_token = "valid.token.here"
        tampered_token = valid_token[:-5] + "hacked"

        # When/Then
        with pytest.raises(ValueError, match="Invalid refresh token"):
            await auth_service.refresh_token(tampered_token)

class TestPasswordHashing:
    """Password Hashing"""

    def test_hash_password_success(self):
        """Test: Hash password successfully"""
        # Given
        password = "SecurePass123"

        # When
        hash_result = hash_password(password)

        # Then
        assert hash_result is not None
        assert hash_result != password
        assert isinstance(hash_result, str)

    def test_verify_password_success(self):
        """Test: Verify password correctly"""
        # Given
        password = "SecurePass123"
        hashed = hash_password(password)

        # When
        result = verify_password(password, hashed)

        # Then
        assert result is True

    def test_verify_password_wrong(self):
        """Test: Verify wrong password"""
        # Given
        password = "SecurePass123"
        wrong_password = "WrongPass123"
        hashed = hash_password(password)

        # When
        result = verify_password(wrong_password, hashed)

        # Then
        assert result is False

    def test_hash_different_salts(self):
        """Test: Same password has different hashes (different salts)"""
        # Given
        password = "SecurePass123"

        # When
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Then
        assert hash1 != hash2  # Different due to salt

    def test_hash_empty_password(self):
        """Test: Hash empty password"""
        # When/Then
        with pytest.raises(ValueError):
            hash_password("")

    def test_hash_very_long_password(self):
        """Test: Hash very long password (>100 chars)"""
        # Given
        password = "a" * 101

        # When/Then
        with pytest.raises(ValueError, match="Password too long"):
            hash_password(password)

    def test_hash_unicode_password(self):
        """Test: Hash password with unicode characters"""
        # Given
        password = "P@sswörd日本語"

        # When
        hash_result = hash_password(password)

        # Then
        assert hash_result is not None
        assert verify_password(password, hash_result) is True

    def test_hash_emoji_password(self):
        """Test: Hash password with emoji"""
        # Given
        password = "P@ssw0rd😀🎉"

        # When
        hash_result = hash_password(password)

        # Then
        assert hash_result is not None
        assert verify_password(password, hash_result) is True

    def test_hash_whitespace_only_password(self):
        """Test: Hash password with only whitespace"""
        # When/Then
        with pytest.raises(ValueError):
            hash_password("   ")

    def test_hash_leading_trailing_spaces(self):
        """Test: Hash password with leading/trailing spaces"""
        # Given
        password = "  SecurePass123  "

        # When
        hash_result = hash_password(password)

        # Then: Should trim spaces
        assert verify_password(password.strip(), hash_result) is True
```

### Code Agent Responsibilities

#### 1.1.3 Implement Auth Service to Pass Tests

**File**: `backend/app/services/auth_service.py`

**Rules**:
1. Read test file ONLY (no test agent thinking)
2. Implement exactly what tests expect
3. Make tests GREEN (all passing)
4. No over-engineering
5. Follow TDD minimal implementation principle

**Implementation Process**:

```python
# backend/app/services/auth_service.py

"""
Auth Service - Implementation

This file implements authentication and user management functionality.
Implementation follows test specifications from test_auth_service.py

Created by: Code Agent (TDD)
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId
import re
import bcrypt
import jwt

from backend.app.core.config import settings
from backend.app.db.database import get_database
from backend.app.core.security import (
    hash_password as core_hash_password,
    verify_password as core_verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)


class AuthService:
    """Authentication service"""

    def __init__(self):
        self.db = get_database()
        self.password_min_length = settings.PASSWORD_MIN_LENGTH
        self.password_max_length = 100

    async def register(
        self,
        email: str,
        password: str,
        name: str
    ) -> Dict:
        """
        Register a new user

        Args:
            email: User email address
            password: User password
            name: User display name

        Returns:
            Dict with success, user, and tokens

        Raises:
            ValueError: If registration fails
        """
        # Validate email format
        if not self._validate_email(email):
            raise ValueError("Invalid email format")

        # Validate password length
        if len(password) < self.password_min_length:
            raise ValueError(f"Password too short (minimum {self.password_min_length} characters)")

        if len(password) > self.password_max_length:
            raise ValueError(f"Password too long (maximum {self.password_max_length} characters)")

        # Check for duplicate email
        existing_user = await self.db.users.find_one({
            "email": email.lower().strip()
        })

        if existing_user:
            raise ValueError("Email already registered")

        # Hash password
        password_hash = core_hash_password(password)

        # Create user
        user_doc = {
            "email": email.lower().strip(),
            "name": name,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)

        # Generate tokens
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": email.lower(),
                "name": name,
                "created_at": user_doc["created_at"]
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }

    async def login(
        self,
        email: str,
        password: str
    ) -> Dict:
        """
        Login user with email and password

        Args:
            email: User email address
            password: User password

        Returns:
            Dict with success, user, and tokens

        Raises:
            ValueError: If login fails
        """
        # Validate email format
        if not self._validate_email(email):
            raise ValueError("Invalid email format")

        # Find user
        user = await self.db.users.find_one({
            "email": email.lower().strip()
        })

        if not user:
            raise ValueError("User not found")

        # Verify password (case-sensitive)
        if not core_verify_password(password, user["password_hash"]):
            # Check for rate limiting
            await self._check_rate_limit(email.lower())

            raise ValueError("Invalid credentials")

        # Check if account is disabled
        if user.get("disabled", False):
            raise ValueError("Account is disabled")

        # Generate tokens
        user_id = str(user["_id"])
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": user["email"],
                "name": user["name"]
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }

    async def refresh_token(
        self,
        refresh_token: str
    ) -> Dict:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            Dict with success and new tokens

        Raises:
            ValueError: If refresh fails
        """
        # Decode refresh token
        try:
            payload = decode_token(refresh_token)
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token")

        # Check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
            raise ValueError("Expired refresh token")

        user_id = payload["sub"]

        # Verify user still exists
        user = await self.db.users.find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            raise ValueError("Invalid refresh token (user not found)")

        # Check if refresh token is revoked
        revoked = await self.db.revoked_tokens.find_one({
            "token": refresh_token
        })

        if revoked:
            raise ValueError("Invalid refresh token (revoked)")

        # Generate new tokens
        access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        return {
            "success": True,
            "tokens": {
                "access_token": access_token,
                "refresh_token": new_refresh_token
            }
        }

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format

        Args:
            email: Email address

        Returns:
            bool: True if valid, False otherwise
        """
        if not email or not email.strip():
            return False

        # Email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        return re.match(pattern, email.strip()) is not None

    async def _check_rate_limit(self, email: str):
        """
        Check and enforce login rate limiting

        Args:
            email: User email address

        Raises:
            ValueError: If rate limit exceeded
        """
        # Count failed login attempts in last 15 minutes
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)

        attempts = await self.db.login_attempts.count_documents({
            "email": email,
            "success": False,
            "timestamp": {"$gte": cutoff_time}
        })

        # Block if 5+ failed attempts
        if attempts >= 5:
            raise ValueError("Too many attempts. Please try again later.")

        # Log this attempt
        await self.db.login_attempts.insert_one({
            "email": email,
            "success": True,
            "timestamp": datetime.utcnow()
        })
```

#### 1.1.4 Refactor Code (After All Tests Pass)

**Refactoring Checklist**:
- [ ] Remove code duplication
- [ ] Improve error messages
- [ ] Add docstrings
- [ ] Optimize database queries
- [ ] Add type hints
- [ ] Ensure code follows PEP8

#### 1.1.5 Verify Tests Still Pass

```bash
# Run all unit tests
cd backend
pytest tests/unit/test_auth_service.py -v

# Expected: All tests passing
# Expected output: 39 passed, 0 failed
```

---

## 📝 Task 1.2: Socket.IO Server Implementation

### Objective
Implement Socket.IO server with Redis integration for real-time collaboration

### Test Agent Responsibilities

#### 1.2.1 Write Socket.IO Tests

**File**: `backend/tests/integration/test_socket_server.py`

**Test Cases** (Must include ALL):

```python
"""
Socket.IO Server Tests - Comprehensive Test Suite

Tests cover:
- Connection/Disconnection
- Workspace joining/leaving
- Presence tracking
- Cursor updates
- Typing indicators
- Yjs CRDT operations
- Task broadcasts
- AI suggestion notifications
- Blocker notifications
- Redis integration
- Error handling
- Edge cases
"""

import pytest
import asyncio
from socketio import AsyncClient
from backend.app.main import app

class TestSocketConnection:
    """Socket.IO Connection Tests"""

    async def test_connect_with_valid_token(self):
        """Test: Connect with valid JWT token"""
        # Given
        token = create_valid_test_token()

        # When
        client = AsyncClient(logger=True, engineio_logger=True)
        await client.connect(
            'http://localhost:8000/socket.io/',
            auth={'token': token}
        )

        # Then
        assert client.connected is True
        await client.disconnect()

    async def test_connect_without_token(self):
        """Test: Connect without token"""
        # When
        client = AsyncClient()
        with pytest.raises(Exception):
            await client.connect('http://localhost:8000/socket.io/')

        # Then
        assert client.connected is False

    async def test_connect_with_invalid_token(self):
        """Test: Connect with invalid token"""
        # Given
        token = "invalid.jwt.token"

        # When/Then
        client = AsyncClient()
        with pytest.raises(Exception):
            await client.connect(
                'http://localhost:8000/socket.io/',
                auth={'token': token}
            )

    async def test_disconnect_gracefully(self):
        """Test: Disconnect gracefully"""
        # Given
        token = create_valid_test_token()
        client = AsyncClient()
        await client.connect('http://localhost:8000/socket.io/', auth={'token': token})

        # When
        await client.disconnect()

        # Then
        assert client.connected is False

    async def test_disconnect_multiple_times(self):
        """Test: Disconnect multiple times (idempotent)"""
        # Given
        token = create_valid_test_token()
        client = AsyncClient()
        await client.connect('http://localhost:8000/socket.io/', auth={'token': token})

        # When: Disconnect twice
        await client.disconnect()
        await client.disconnect()

        # Then: Should not raise error
        assert client.connected is False

class TestWorkspaceJoinLeave:
    """Workspace Join/Leave Tests"""

    async def test_join_workspace_valid(self):
        """Test: Join workspace with valid token"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        # When
        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await asyncio.sleep(0.1)  # Wait for event

        # Then
        assert client1.sid is not None
        await client1.disconnect()
        await client2.disconnect()

    async def test_join_workspace_not_member(self):
        """Test: Join workspace user is not member of"""
        # Given
        client = await create_authenticated_client()
        workspace_id = "random_workspace_id"

        # When/Then
        with pytest.raises(Exception):
            await client.emit('join_workspace', {'workspace_id': workspace_id})

        await client.disconnect()

    async def test_join_workspace_invalid_token(self):
        """Test: Join workspace with invalid token"""
        # Given
        client = AsyncClient()
        workspace_id = create_test_workspace()

        # When/Then
        with pytest.raises(Exception):
            await client.emit('join_workspace', {'workspace_id': workspace_id})

    async def test_leave_workspace(self):
        """Test: Leave workspace"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()
        await client.emit('join_workspace', {'workspace_id': workspace_id})

        # When
        await client.emit('leave_workspace', {'workspace_id': workspace_id})
        await asyncio.sleep(0.1)

        # Then
        # Verify user removed from workspace
        presence = await get_workspace_presence(workspace_id)
        assert client.sid not in presence

        await client.disconnect()

class TestPresenceTracking:
    """Presence Tracking Tests"""

    async def test_presence_update_on_join(self):
        """Test: Presence updates when user joins"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        # Track presence updates
        presence_updates = []
        def on_presence_update(data):
            presence_updates.append(data)

        client2.on('presence_update', on_presence_update)

        # When
        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await asyncio.sleep(0.1)

        # Then
        assert len(presence_updates) > 0
        assert presence_updates[-1]['status'] == 'online'

        await client1.disconnect()
        await client2.disconnect()

    async def test_presence_update_on_leave(self):
        """Test: Presence updates when user leaves"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        await client1.emit('join_workspace', {'workspace_id': workspace_id})

        presence_updates = []
        client2.on('presence_update', lambda data: presence_updates.append(data))

        # When
        await client1.emit('leave_workspace', {'workspace_id': workspace_id})
        await asyncio.sleep(0.1)

        # Then
        assert any(p['status'] == 'offline' for p in presence_updates)

        await client1.disconnect()
        await client2.disconnect()

    async def test_presence_multiple_users(self):
        """Test: Presence tracking with multiple users"""
        # Given
        clients = [await create_authenticated_client() for _ in range(5)]
        workspace_id = create_test_workspace()

        # When: All join workspace
        for client in clients:
            await client.emit('join_workspace', {'workspace_id': workspace_id})

        await asyncio.sleep(0.1)

        # Then
        presence = await get_workspace_presence(workspace_id)
        assert len(presence) == 5

        for client in clients:
            await client.disconnect()

    async def test_presence_timeout(self):
        """Test: Presence times out after inactivity"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()
        await client.emit('join_workspace', {'workspace_id': workspace_id})

        # When: Simulate 6 minutes of inactivity
        await asyncio.sleep(360)  # 6 minutes

        # Then
        presence = await get_workspace_presence(workspace_id)
        assert client.sid not in presence  # Should be removed

        await client.disconnect()

class TestCursorTracking:
    """Cursor Position Tracking Tests"""

    async def test_cursor_update_broadcast(self):
        """Test: Cursor update broadcasts to other users"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await client2.emit('join_workspace', {'workspace_id': workspace_id})

        cursor_updates = []
        client2.on('cursor_update', lambda data: cursor_updates.append(data))

        # When
        await client1.emit('cursor_update', {
            'workspace_id': workspace_id,
            'document_id': 'doc1',
            'position': {'x': 100, 'y': 200}
        })
        await asyncio.sleep(0.1)

        # Then
        assert len(cursor_updates) > 0
        assert cursor_updates[0]['user_id'] == get_user_id_from_client(client1)

        await client1.disconnect()
        await client2.disconnect()

    async def test_cursor_update_not_to_self(self):
        """Test: Cursor update does not broadcast to sender"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()
        await client.emit('join_workspace', {'workspace_id': workspace_id})

        cursor_updates = []
        client.on('cursor_update', lambda data: cursor_updates.append(data))

        # When
        await client.emit('cursor_update', {
            'workspace_id': workspace_id,
            'document_id': 'doc1',
            'position': {'x': 100, 'y': 200}
        })
        await asyncio.sleep(0.1)

        # Then
        assert len(cursor_updates) == 0  # Should not receive own cursor

        await client.disconnect()

    async def test_cursor_update_multiple_positions(self):
        """Test: Cursor updates handle multiple positions rapidly"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await client2.emit('join_workspace', {'workspace_id': workspace_id})

        cursor_updates = []
        client2.on('cursor_update', lambda data: cursor_updates.append(data))

        # When: Send multiple cursor updates rapidly
        for i in range(10):
            await client1.emit('cursor_update', {
                'workspace_id': workspace_id,
                'document_id': 'doc1',
                'position': {'x': i * 10, 'y': i * 20}
            })
            await asyncio.sleep(0.01)

        # Then
        assert len(cursor_updates) == 10

        await client1.disconnect()
        await client2.disconnect()

class TestTypingIndicator:
    """Typing Indicator Tests"""

    async def test_typing_indicator_broadcast(self):
        """Test: Typing indicator broadcasts to others"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await client2.emit('join_workspace', {'workspace_id': workspace_id})

        typing_updates = []
        client2.on('typing_indicator', lambda data: typing_updates.append(data))

        # When
        await client1.emit('typing_indicator', {
            'workspace_id': workspace_id,
            'is_typing': True
        })
        await asyncio.sleep(0.1)

        # Then
        assert len(typing_updates) > 0
        assert typing_updates[0]['is_typing'] is True

        await client1.disconnect()
        await client2.disconnect()

    async def test_typing_indicator_stop(self):
        """Test: Typing indicator stops"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await client2.emit('join_workspace', {'workspace_id': workspace_id})

        typing_updates = []
        client2.on('typing_indicator', lambda data: typing_updates.append(data))

        # When
        await client1.emit('typing_indicator', {
            'workspace_id': workspace_id,
            'is_typing': False
        })
        await asyncio.sleep(0.1)

        # Then
        assert len(typing_updates) > 0
        assert typing_updates[-1]['is_typing'] is False

        await client1.disconnect()
        await client2.disconnect()

class TestYjsCRDT:
    """Yjs CRDT Operation Tests"""

    async def test_ydoc_sync_broadcast(self):
        """Test: Yjs CRDT ops broadcast to workspace"""
        # Given
        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()
        document_id = 'test_doc'

        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await client2.emit('join_workspace', {'workspace_id': workspace_id})

        ydoc_updates = []
        client2.on('ydoc_update', lambda data: ydoc_updates.append(data))

        # When
        ops = bytes([1, 2, 3, 4, 5])  # Binary CRDT ops
        await client1.emit('ydoc_sync', {
            'workspace_id': workspace_id,
            'document_id': document_id,
            'ops': ops
        })
        await asyncio.sleep(0.1)

        # Then
        assert len(ydoc_updates) > 0
        assert ydoc_updates[0]['document_id'] == document_id
        assert ydoc_updates[0]['ops'] == ops

        await client1.disconnect()
        await client2.disconnect()

    async def test_ydoc_offline_queue(self):
        """Test: Yjs ops queued when offline"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()

        # When: Client goes offline, edits, comes back online
        await client.disconnect()

        # Simulate offline edits
        offline_ops = [
            bytes([1, 2, 3]),
            bytes([4, 5, 6])
        ]

        # Reconnect
        await client.connect()

        # Then: Should sync offline ops
        for op in offline_ops:
            await client.emit('ydoc_sync', {
                'workspace_id': workspace_id,
                'document_id': 'test_doc',
                'ops': op
            })

        await client.disconnect()

class TestRedisIntegration:
    """Redis Integration Tests"""

    async def test_redis_presence_storage(self):
        """Test: Presence stored in Redis"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()

        # When
        await client.emit('join_workspace', {'workspace_id': workspace_id})
        await asyncio.sleep(0.1)

        # Then: Verify stored in Redis
        presence_key = f"presence:{workspace_id}:{client.sid}"
        presence = await redis_client.hgetall(presence_key)

        assert presence is not None
        assert presence['status'] == 'online'

        await client.disconnect()

    async def test_redis_presence_expiry(self):
        """Test: Presence expires after TTL"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()

        await client.emit('join_workspace', {'workspace_id': workspace_id})
        presence_key = f"presence:{workspace_id}:{client.sid}"

        # When: Wait for expiry (6 minutes)
        await asyncio.sleep(360)

        # Then
        presence = await redis_client.get(presence_key)
        assert presence is None

        await client.disconnect()

    async def test_redis_pubsub_broadcast(self):
        """Test: Redis pub/sub for cross-instance broadcast"""
        # Given: Two Socket.IO server instances (simulated)
        # This would require actual multi-instance setup
        # For now, test basic pub/sub functionality

        client1 = await create_authenticated_client()
        client2 = await create_authenticated_client()
        workspace_id = create_test_workspace()

        # When
        await client1.emit('join_workspace', {'workspace_id': workspace_id})
        await asyncio.sleep(0.1)

        # Then: Should broadcast via Redis pub/sub
        await client1.disconnect()
        await client2.disconnect()

class TestErrorHandling:
    """Error Handling Tests"""

    async def test_invalid_event_payload(self):
        """Test: Invalid event payload handled gracefully"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()

        # When: Send invalid payload
        await client.emit('join_workspace', {'invalid': 'payload'})
        await asyncio.sleep(0.1)

        # Then: Should not crash
        assert client.connected is True

        await client.disconnect()

    async def test_malformed_binary_data(self):
        """Test: Malformed binary CRDT ops handled"""
        # Given
        client = await create_authenticated_client()
        workspace_id = create_test_workspace()

        # When: Send malformed binary data
        await client.emit('ydoc_sync', {
            'workspace_id': workspace_id,
            'document_id': 'test_doc',
            'ops': "not binary data"
        })

        # Then: Should not crash
        assert client.connected is True

        await client.disconnect()

    async def test_redis_connection_failure(self):
        """Test: Redis connection failure handled gracefully"""
        # Given: Mock Redis failure
        # This would require mocking Redis client

        # When: Try to store presence
        # Then: Should fall back gracefully
        # (Implementation depends on actual error handling strategy)
```

### Code Agent Responsibilities

#### 1.2.2 Implement Socket.IO Server

**File**: `backend/app/api/socket_server.py`

**Implementation Process**:
1. Read test file ONLY
2. Implement event handlers
3. Make tests GREEN
4. Refactor for quality

**Implementation Structure**:
```python
# backend/app/api/socket_server.py

"""
Socket.IO Server Implementation

Implements real-time collaboration features:
- Connection/Disconnection
- Workspace join/leave
- Presence tracking
- Cursor updates
- Typing indicators
- Yjs CRDT operations

Created by: Code Agent (TDD)
"""

import socketio
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from backend.app.core.config import settings
from backend.app.db.database import get_redis
from backend.app.api.dependencies import validate_token

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Redis manager
redis_client = get_redis()
sio_manager = socketio.AsyncRedisManager(
    settings.REDIS_URL,
    pubsub='socketio'
)

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    client_manager=sio_manager
)


def register_socket_events(sio: socketio.AsyncServer):
    """Register all Socket.IO event handlers"""

    @sio.event
    async def connect(sid, environ):
        """Handle client connection"""
        # Extract token from query or headers
        auth_token = environ.get('HTTP_AUTHORIZATION')
        if not auth_token:
            return False  # Reject connection

        # Validate token
        try:
            payload = validate_token(auth_token)
            user_id = payload['sub']
        except Exception:
            return False  # Reject connection

        # Store user in session
        await sio.save_session(sid, {
            'user_id': user_id,
            'connected_at': datetime.utcnow()
        })

        print(f"Client connected: {sid}, user_id: {user_id}")

    @sio.event
    async def disconnect(sid):
        """Handle client disconnection"""
        session = await sio.get_session(sid)

        if session:
            user_id = session.get('user_id')

            # Remove from all workspaces
            await _remove_user_from_all_workspaces(user_id)

            print(f"Client disconnected: {sid}, user_id: {user_id}")

    @sio.event
    async def join_workspace(sid, data):
        """Handle workspace join"""
        workspace_id = data.get('workspace_id')

        if not workspace_id:
            await sio.emit('error', {'message': 'workspace_id required'}, room=sid)
            return

        session = await sio.get_session(sid)
        user_id = session.get('user_id')

        # Verify user is member (simplified - would check DB)
        # For now, allow all authenticated users

        # Join room
        sio.enter_room(sid, workspace_id)

        # Update presence
        await _update_presence(user_id, workspace_id, 'online')

        # Broadcast presence update
        await sio.emit(
            'presence_update',
            {
                'user_id': user_id,
                'status': 'online',
                'workspace_id': workspace_id,
                'timestamp': str(datetime.utcnow())
            },
            room=workspace_id,
            skip_sid=sid
        )

        print(f"User {user_id} joined workspace {workspace_id}")

    @sio.event
    async def leave_workspace(sid, data):
        """Handle workspace leave"""
        workspace_id = data.get('workspace_id')

        if not workspace_id:
            return

        session = await sio.get_session(sid)
        user_id = session.get('user_id')

        # Leave room
        sio.leave_room(sid, workspace_id)

        # Update presence
        await _update_presence(user_id, workspace_id, 'offline')

        # Broadcast presence update
        await sio.emit(
            'presence_update',
            {
                'user_id': user_id,
                'status': 'offline',
                'workspace_id': workspace_id,
                'timestamp': str(datetime.utcnow())
            },
            room=workspace_id
        )

        print(f"User {user_id} left workspace {workspace_id}")

    @sio.event
    async def cursor_update(sid, data):
        """Handle cursor position updates"""
        workspace_id = data.get('workspace_id')
        document_id = data.get('document_id')
        position = data.get('position')

        session = await sio.get_session(sid)
        user_id = session.get('user_id')

        if not all([workspace_id, document_id, position]):
            return

        # Broadcast to others in workspace
        await sio.emit(
            'cursor_update',
            {
                'user_id': user_id,
                'document_id': document_id,
                'position': position,
                'timestamp': str(datetime.utcnow())
            },
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def typing_indicator(sid, data):
        """Handle typing indicators"""
        workspace_id = data.get('workspace_id')
        is_typing = data.get('is_typing', False)

        session = await sio.get_session(sid)
        user_id = session.get('user_id')

        if not workspace_id:
            return

        # Broadcast to workspace
        await sio.emit(
            'typing_indicator',
            {
                'user_id': user_id,
                'is_typing': is_typing,
                'timestamp': str(datetime.utcnow())
            },
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def ydoc_sync(sid, data):
        """Handle Yjs CRDT operations"""
        workspace_id = data.get('workspace_id')
        document_id = data.get('document_id')
        ops = data.get('ops')

        session = await sio.get_session(sid)
        user_id = session.get('user_id')

        if not all([workspace_id, document_id, ops]):
            await sio.emit('error', {'message': 'Missing required fields'}, room=sid)
            return

        # Validate binary data
        if not isinstance(ops, (bytes, bytearray)):
            await sio.emit('error', {'message': 'ops must be binary'}, room=sid)
            return

        # Store in database (simplified)
        await _store_crdt_ops(document_id, ops, user_id)

        # Broadcast to others
        await sio.emit(
            'ydoc_update',
            {
                'document_id': document_id,
                'ops': ops,
                'timestamp': str(datetime.utcnow())
            },
            room=workspace_id,
            skip_sid=sid
        )

        print(f"Yjs ops synced for document {document_id} by user {user_id}")


# Helper functions

async def _update_presence(user_id: str, workspace_id: str, status: str):
    """Update user presence in Redis"""
    key = f"presence:{workspace_id}:{user_id}"

    value = {
        'user_id': user_id,
        'workspace_id': workspace_id,
        'status': status,
        'last_seen': str(datetime.utcnow())
    }

    await redis_client.hset(key, mapping=value)
    await redis_client.expire(key, 300)  # 5 minute TTL


async def _remove_user_from_all_workspaces(user_id: str):
    """Remove user from all workspace presences"""
    # Find all presence keys for user
    pattern = f"presence:*:{user_id}"
    keys = await redis_client.keys(pattern)

    for key in keys:
        await redis_client.delete(key)


async def _store_crdt_ops(document_id: str, ops: bytes, user_id: str):
    """Store CRDT operations in database"""
    # In real implementation, this would store in MongoDB
    # For now, just log
    print(f"Storing CRDT ops for document {document_id}")
```

#### 1.2.3 Register Socket Server in Main

**File**: `backend/app/main.py` (modify)

```python
# Add to backend/app/main.py
from socketio import ASGIApp
from backend.app.api.socket_server import sio, register_socket_events

# Register socket events
register_socket_events(sio)

# Create Socket.IO ASGI app
socket_app = ASGIApp(sio)

# Mount to FastAPI
app.mount("/socket.io", socket_app)
```

---

## 📝 Task 1.3: AI Service MVP

### Objective
Implement AI microservice for task rewriting with OpenAI integration

### Test Agent Responsibilities

#### 1.3.1 Write AI Service Tests

**File**: `ai-service/tests/test_ai_service.py`

**Test Cases**:

```python
"""
AI Service Tests - Comprehensive Test Suite

Tests cover:
- Heuristic rule-based suggestions
- Local classifier fallback
- OpenAI cloud LLM integration
- Redis caching
- JSON schema validation
- Confidence scoring
- Error handling
- Edge cases
"""

import pytest
import asyncio
from httpx import AsyncClient
from main import app

class TestAIServiceHealth:
    """AI Service Health Tests"""

    async def test_health_check(self):
        """Test: Health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "service" in data
            assert "version" in data

class TestTaskRewrite:
    """Task Rewrite Tests"""

    async def test_rewrite_task_simple(self):
        """Test: Rewrite simple task"""
        payload = {
            "raw_title": "Fix landing page",
            "raw_description": "Conversion rate is low",
            "context": {"workspace_type": "marketing"}
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            assert response.status_code == 200
            data = response.json()

            assert "rewritten_title" in data
            assert "checklist" in data
            assert "suggested_priority" in data
            assert "confidence" in data
            assert "explanation" in data

    async def test_rewrite_task_with_heuristics(self):
        """Test: Rewrite task using heuristics"""
        payload = {
            "raw_title": "Fix urgent bug",
            "raw_description": "ASAP"
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            data = response.json()

            # Should detect urgency from keywords
            assert data["suggested_priority"] >= 4
            assert "urgency" in data["explanation"].lower()

    async def test_rewrite_task_vague(self):
        """Test: Rewrite vague task"""
        payload = {
            "raw_title": "Write code",
            "raw_description": ""
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            data = response.json()

            # Should have low confidence
            assert data["confidence"] < 0.5
            assert "vague" in data["explanation"].lower()
            # May return null for rewritten_title
            if data.get("rewritten_title") is None:
                assert data["confidence"] < 0.5

    async def test_rewrite_task_with_due_date(self):
        """Test: Rewrite task with due date"""
        payload = {
            "raw_title": "Complete by Friday",
            "raw_description": "End of week"
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            data = response.json()

            # Should extract due date
            assert "suggested_due_date" in data
            if data["suggested_due_date"]:
                assert isinstance(data["suggested_due_date"], str)

    async def test_rewrite_task_invalid_json(self):
        """Test: Rewrite task returns invalid JSON from LLM"""
        # Mock OpenAI to return invalid JSON
        # Then verify fallback to heuristics
        pass

    async def test_rewrite_task_empty_fields(self):
        """Test: Rewrite task with empty fields"""
        payload = {
            "raw_title": "",
            "raw_description": ""
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            # Should return error
            assert response.status_code == 422

    async def test_rewrite_task_long_title(self):
        """Test: Rewrite task with very long title"""
        payload = {
            "raw_title": "a" * 201,  # > 200 chars
            "raw_description": "test"
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            assert response.status_code == 422

    async def test_rewrite_task_with_context(self):
        """Test: Rewrite task with workspace context"""
        payload = {
            "raw_title": "Design feature",
            "raw_description": "For marketing campaign",
            "context": {
                "workspace_type": "marketing",
                "team_velocity": "high",
                "available_capacity": "2 weeks"
            }
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            data = response.json()

            # Should use context in suggestion
            assert data["confidence"] > 0.6  # Higher with context

    async def test_rewrite_task_checklist_generation(self):
        """Test: Rewrite generates appropriate checklist"""
        payload = {
            "raw_title": "Fix landing page bug",
            "raw_description": "Users can't sign up"
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            data = response.json()

            # Should generate actionable checklist
            assert isinstance(data["checklist"], list)
            assert len(data["checklist"]) >= 3
            assert len(data["checklist"]) <= 6  # Max 6 items

class TestRedisCaching:
    """Redis Caching Tests"""

    async def test_cache_hit(self):
        """Test: Cache hit on identical task"""
        payload = {
            "raw_title": "Fix landing page",
            "raw_description": "Conversion rate low",
            "context": {}
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            # First request
            response1 = await client.post("/api/v1/ai/rewrite", json=payload)
            data1 = response1.json()

            # Second request (should hit cache)
            response2 = await client.post("/api/v1/ai/rewrite", json=payload)
            data2 = response2.json()

            # Results should be identical
            assert data1 == data2

    async def test_cache_miss(self):
        """Test: Cache miss on different task"""
        payload1 = {"raw_title": "Task A", "raw_description": ""}
        payload2 = {"raw_title": "Task B", "raw_description": ""}

        async with AsyncClient(app=app, base_url="http://test") as client:
            response1 = await client.post("/api/v1/ai/rewrite", json=payload1)
            data1 = response1.json()

            response2 = await client.post("/api/v1/ai/rewrite", json=payload2)
            data2 = response2.json()

            # Results should be different
            assert data1 != data2

    async def test_cache_expiry(self):
        """Test: Cache expires after TTL"""
        # Set short TTL for testing
        # Request task
        # Wait for expiry
        # Request again - should be cache miss
        pass

class TestConfidenceScoring:
    """Confidence Scoring Tests"""

    async def test_confidence_high(self):
        """Test: High confidence (> 0.8)"""
        payload = {
            "raw_title": "Fix critical bug affecting production",
            "raw_description": "Users cannot sign up"
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)
            data = response.json()

            assert data["confidence"] >= 0.8

    async def test_confidence_medium(self):
        """Test: Medium confidence (0.5 - 0.8)"""
        payload = {
            "raw_title": "Fix bug",
            "raw_description": ""
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)
            data = response.json()

            assert 0.5 <= data["confidence"] < 0.8

    async def test_confidence_low(self):
        """Test: Low confidence (< 0.5)"""
        payload = {
            "raw_title": "Do something",
            "raw_description": ""
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)
            data = response.json()

            assert data["confidence"] < 0.5

class TestPrioritization:
    """Task Prioritization Tests"""

    async def test_prioritize_tasks(self):
        """Test: Prioritize multiple tasks"""
        payload = {
            "task_ids": ["task1", "task2", "task3"],
            "context": {"workspace_id": "ws1"}
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/prioritize", json=payload)

            assert response.status_code == 200
            data = response.json()

            assert "prioritized_tasks" in data
            assert "scores" in data
            assert len(data["prioritized_tasks"]) == 3

    async def test_prioritize_empty_list(self):
        """Test: Prioritize empty task list"""
        payload = {
            "task_ids": [],
            "context": {}
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/prioritize", json=payload)

            data = response.json()

            assert data["prioritized_tasks"] == []

class TestErrorHandling:
    """Error Handling Tests"""

    async def test_openai_rate_limit(self):
        """Test: OpenAI rate limit handled"""
        # Mock OpenAI rate limit response
        # Verify fallback to heuristics
        pass

    async def test_openai_timeout(self):
        """Test: OpenAI timeout handled"""
        # Mock OpenAI timeout
        # Verify fallback to heuristics
        pass

    async def test_redis_connection_failure(self):
        """Test: Redis connection failure handled"""
        # Mock Redis failure
        # Verify AI service still works (without cache)
        pass

    async def test_malformed_input(self):
        """Test: Malformed input handled"""
        payload = {
            "raw_title": 123,  # Should be string
            "raw_description": None
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/ai/rewrite", json=payload)

            # Should return validation error
            assert response.status_code == 422
```

### Code Agent Responsibilities

#### 1.3.2 Implement AI Service

**File**: `ai-service/app/services/ai_service.py`

**Implementation Process**:
1. Read test file ONLY
2. Implement heuristics engine
3. Implement local classifier
4. Implement OpenAI integration
5. Make all tests GREEN
6. Refactor for quality

---

## 📝 Task 1.4: Celery Workers

### Objective
Implement Celery workers for background job processing

### Test Agent Responsibilities

#### 1.4.1 Write Celery Worker Tests

**File**: `backend/tests/integration/test_celery_workers.py`

**Test Cases**:

```python
"""
Celery Workers Tests - Comprehensive Test Suite

Tests cover:
- Task creation triggers AI suggestion
- Blocker detection worker
- Cleanup jobs
- Job scheduling
- Error handling and retries
- Redis queue management
"""

import pytest
from backend.app.celery_app import celery_app
from backend.app.workers.ai_tasks import process_ai_suggestion
from backend.app.workers.blocker_tasks import detect_workspace_blockers

class TestCeleryAISuggestion:
    """AI Suggestion Worker Tests"""

    def test_process_ai_suggestion_success(self):
        """Test: Process AI suggestion task successfully"""
        task = process_ai_suggestion.apply_async(
            args=['task_123', 'Fix landing page', 'Low conversion']
        )

        result = task.get(timeout=30)

        assert result['status'] == 'success'
        assert result['task_id'] == 'task_123'
        assert 'suggestion' in result

    def test_process_ai_suggestion_retry_on_failure(self):
        """Test: Retry on AI service failure"""
        # Mock AI service failure
        # Verify task retries
        pass

    def test_process_ai_suggestion_timeout(self):
        """Test: Handle AI service timeout"""
        # Mock AI service timeout
        # Verify graceful handling
        pass

class TestCeleryBlockerDetection:
    """Blocker Detection Worker Tests"""

    def test_detect_blockers_success(self):
        """Test: Detect blockers successfully"""
        task = detect_workspace_blockers.apply_async(
            args=['workspace_123']
        )

        result = task.get(timeout=60)

        assert result['status'] == 'success'
        assert 'blocked_count' in result

    def test_detect_blockers_no_tasks(self):
        """Test: Handle workspace with no tasks"""
        task = detect_workspace_blockers.apply_async(
            args=['empty_workspace']
        )

        result = task.get(timeout=60)

        assert result['status'] == 'success'
        assert result['blocked_count'] == 0

    def test_detect_blockers_periodic(self):
        """Test: Blocker detection runs periodically"""
        # Verify Celery Beat schedule
        # Check task runs every 5 minutes
        pass

class TestCeleryCleanup:
    """Cleanup Worker Tests"""

    def test_cleanup_old_suggestions(self):
        """Test: Cleanup old AI suggestions"""
        from backend.app.workers.ai_tasks import cleanup_old_suggestions

        task = cleanup_old_suggestions.apply_async()

        result = task.get(timeout=60)

        assert result['status'] == 'success'
        assert 'deleted_count' in result

class TestCeleryJobQueue:
    """Job Queue Management Tests"""

    def test_job_queued_successfully(self):
        """Test: Jobs are queued correctly"""
        # Queue multiple jobs
        # Verify queue depth
        pass

    def test_job_priority(self):
        """Test: Job priority is respected"""
        # Queue jobs with different priorities
        # Verify high priority jobs run first
        pass

class TestCeleryErrorHandling:
    """Error Handling Tests"""

    def test_worker_crash_recovery(self):
        """Test: Worker recovers from crash"""
        # Simulate worker crash
        # Verify task is requeued
        pass

    def test_redis_broker_failure(self):
        """Test: Handle Redis broker failure"""
        # Mock Redis failure
        # Verify graceful degradation
        pass

    def test_task_result_backend_failure(self):
        """Test: Handle result backend failure"""
        # Mock result backend failure
        # Verify task completion logging
        pass
```

### Code Agent Responsibilities

#### 1.4.2 Implement Celery Workers

**File**: `backend/app/workers/ai_tasks.py`

**Implementation Process**:
1. Read test file ONLY
2. Implement AI suggestion task
3. Implement cleanup task
4. Implement blocker detection task
5. Make all tests GREEN
6. Refactor for quality

---

## 🔄 Execution Protocol

### Step-by-Step Workflow

#### Step 1: Setup (Both Agents)

**Test Agent**:
```bash
# 1. Read PRD and phase documentation
cd docs/
read PHASE1_CRITICAL_BACKEND.md

# 2. Understand task requirements
# 3. Review existing code
cd ../backend
```

**Code Agent**:
```bash
# 1. Prepare development environment
cd backend
source venv/bin/activate

# 2. Verify test framework
pytest --version

# 3. Ready to receive test files
```

#### Step 2: RED Phase - Test Agent Only

**Test Agent Actions**:
1. Choose task (e.g., 1.1.1)
2. Read requirements
3. Identify ALL edge cases
4. Write failing tests
5. Save test file
6. Document edge cases

**Output**: Test file (RED state - all tests fail)

**Example**:
```python
# backend/tests/unit/test_auth_service.py
# Test Agent writes this file
# All tests should FAIL initially

def test_register_user_success(self):
    assert False  # Will fail, expects implementation
```

#### Step 3: GREEN Phase - Code Agent Only

**Code Agent Actions**:
1. Read test file (NO Test Agent thinking)
2. Understand test expectations
3. Write minimal code to pass
4. Run tests
5. Fix until GREEN

**Rules**:
- DO NOT read Test Agent's notes
- DO NOT read Test Agent's reasoning
- ONLY read test file code
- Implement EXACTLY what tests expect

**Output**: Implementation code (GREEN state - all tests pass)

#### Step 4: REFACTOR Phase - Code Agent

**Code Agent Actions**:
1. Review code quality
2. Remove duplication
3. Add documentation
4. Improve design
5. Run tests (must stay GREEN)

**Rules**:
- No new features
- Only code quality improvements
- Tests must still pass

#### Step 5: VALIDATE Phase - Test Agent

**Test Agent Actions**:
1. Run all tests
2. Verify 100% pass rate
3. Check test coverage
4. Look for missed edge cases
5. Document results

**Output**: Test report + coverage metrics

---

## 📊 Success Criteria

### Phase 1 Success Metrics

- [ ] All 39 unit tests passing (100%)
- [ ] Socket.IO tests passing (15/15)
- [ ] AI service tests passing (12/12)
- [ ] Celery worker tests passing (8/8)
- [ ] Test coverage > 80%
- [ ] No code duplication
- [ ] All code documented
- [ ] PEP8 compliant

### Edge Cases Coverage

Each test suite must include:
- ✅ Happy path (normal operation)
- ✅ Sad path (error conditions)
- ✅ Boundary values (min/max)
- ✅ Empty/null inputs
- ✅ Invalid formats
- ✅ Timeout scenarios
- ✅ Race conditions (where applicable)
- ✅ Resource exhaustion (where applicable)
- ✅ Network failures (where applicable)

---

## 🛠️ Agent Communication Protocol

### File Sharing Convention

**Test Agent Creates**:
```
backend/tests/unit/test_auth_service.py
backend/tests/integration/test_socket_server.py
ai-service/tests/test_ai_service.py
backend/tests/integration/test_celery_workers.py
```

**Code Agent Reads**:
```
backend/tests/unit/test_auth_service.py (ONLY)
backend/tests/integration/test_socket_server.py (ONLY)
ai-service/tests/test_ai_service.py (ONLY)
backend/tests/integration/test_celery_workers.py (ONLY)
```

### Information Flow

```
┌─────────────────────────────────────────────────────────┐
│               TEST AGENT                           │
│  ┌───────────────────────────────────────────┐   │
│  │ 1. Write test file with ALL cases      │   │
│  │ 2. Save to backend/tests/              │   │
│  │ 3. NO communication with Code Agent    │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↓
                    (File saved)
                         ↓
┌─────────────────────────────────────────────────────────┐
│              CODE AGENT                           │
│  ┌───────────────────────────────────────────┐   │
│  │ 1. Read test file ONLY                 │   │
│  │ 2. Implement code to pass tests       │   │
│  │ 3. Run tests                          │   │
│  │ 4. NO communication with Test Agent   │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↓
                    (Tests pass)
                         ↓
┌─────────────────────────────────────────────────────────┐
│               TEST AGENT (Validate)                │
│  ┌───────────────────────────────────────────┐   │
│  │ 1. Run all tests                       │   │
│  │ 2. Verify 100% pass rate              │   │
│  │ 3. Check coverage                      │   │
│  │ 4. Look for missed edge cases          │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Independence Rules

**STRICT RULES**:

1. **Test Agent NEVER shares**:
   - ❌ Thinking process
   - ❌ Reasoning for test cases
   - ❌ Notes or comments
   - ❌ Implementation suggestions
   - ❌ Design decisions

2. **Code Agent NEVER sees**:
   - ❌ Test Agent's thoughts
   - ❌ Test Agent's notes
   - ❌ Test Agent's reasoning
   - ❌ ANY documentation from Test Agent

3. **ONLY communication**:
   - ✅ Test file code (Python/TypeScript)
   - ✅ Test file location
   - ✅ NOTHING ELSE

4. **Code Agent MUST**:
   - ✅ Read test file ONLY
   - ✅ Implement exactly what tests expect
   - ✅ Make tests GREEN
   - ✅ Refactor after GREEN

---

## 📅 Execution Timeline

### Week 1: Task 1.1 - Fix Unit Tests

| Day | Test Agent | Code Agent |
|------|------------|------------|
| Mon | Analyze failing tests (2h) | Setup environment (1h) |
| Tue | Rewrite auth tests (2h) | Implement auth fixes (3h) |
| Wed | Rewrite task tests (2h) | Implement task fixes (3h) |
| Thu | Rewrite CRDT tests (2h) | Implement CRDT fixes (2h) |
| Fri | Validate all tests (2h) | Refactor code (2h) |

**Deliverable**: 39/39 unit tests passing

### Week 2: Task 1.2 - Socket.IO

| Day | Test Agent | Code Agent |
|------|------------|------------|
| Mon | Write connection tests (3h) | Implement connection (4h) |
| Tue | Write workspace tests (3h) | Implement workspace (4h) |
| Wed | Write presence tests (3h) | Implement presence (4h) |
| Thu | Write CRDT tests (3h) | Implement CRDT (4h) |
| Fri | Validate all tests (2h) | Refactor code (2h) |

**Deliverable**: Socket.IO server fully functional

### Week 3: Task 1.3 - AI Service

| Day | Test Agent | Code Agent |
|------|------------|------------|
| Mon | Write rewrite tests (3h) | Implement rewrite (4h) |
| Tue | Write heuristics tests (2h) | Implement heuristics (3h) |
| Wed | Write caching tests (2h) | Implement caching (3h) |
| Thu | Write prioritization tests (2h) | Implement prioritization (3h) |
| Fri | Validate all tests (2h) | Refactor code (2h) |

**Deliverable**: AI service fully functional

### Week 4: Task 1.4 - Celery Workers

| Day | Test Agent | Code Agent |
|------|------------|------------|
| Mon | Write AI worker tests (2h) | Implement AI worker (3h) |
| Tue | Write blocker tests (2h) | Implement blocker (3h) |
| Wed | Write cleanup tests (2h) | Implement cleanup (2h) |
| Thu | Write queue tests (2h) | Implement queue (2h) |
| Fri | Validate all tests (2h) | Refactor code (2h) |

**Deliverable**: Celery workers fully functional

---

## ✅ Pre-Execution Checklist

### Test Agent Setup

- [ ] Read and understood PRD
- [ ] Read Phase 1 documentation
- [ ] Reviewed existing codebase
- [ ] Identified all edge cases for Task 1.1
- [ ] Prepared test file structure
- [ ] Ready to write tests

### Code Agent Setup

- [ ] Development environment configured
- [ ] Python virtual environment activated
- [ ] Dependencies installed
- [ ] Test framework ready
- [ ] Ready to read test files

### Third-Party Services

- [ ] OpenAI API key obtained
- [ ] Added to `.env` file
- [ ] MongoDB running (docker-compose)
- [ ] Redis running (docker-compose)
- [ ] Backend server ready

---

## 📞 Coordination Mechanism

### File-Based Handoff

**Test Agent → Code Agent**:
1. Test Agent writes test file
2. Test Agent saves to specific location
3. Test Agent notifies: "Test file ready at: backend/tests/unit/test_auth_service.py"
4. Code Agent reads test file
5. Code Agent implements code
6. Code Agent runs tests
7. Code Agent notifies: "Tests passing for: backend/tests/unit/test_auth_service.py"

**Code Agent → Test Agent**:
1. Code Agent implements code
2. Code Agent runs tests
3. Code Agent fixes until GREEN
4. Code Agent notifies: "All tests passing"
5. Test Agent validates
6. Test Agent runs full test suite
7. Test Agent notifies: "Validation complete - all tests pass"

### Minimal Communication Protocol

**Allowed**:
- ✅ File location messages
- ✅ Test result summaries
- ✅ "READY" / "DONE" status
- ✅ Error reports (with file + line number)

**NOT Allowed**:
- ❌ Thinking process sharing
- ❌ Reasoning explanations
- ❌ Design discussions
- ❌ Implementation suggestions
- ❌ Anything other than file/status

---

## 🎯 Success Definition

### Phase 1 Complete When:

✅ **All Tests Passing**:
- 39/39 unit tests pass
- 15/15 Socket.IO tests pass
- 12/12 AI service tests pass
- 8/8 Celery worker tests pass

✅ **Code Quality**:
- Black formatted
- Flake8 clean
- Type hints complete
- Docstrings present
- No code duplication

✅ **Test Coverage**:
- > 80% code coverage
- All critical paths tested
- All edge cases covered

✅ **Functional Requirements**:
- Real-time collaboration working
- AI suggestions functional
- Background jobs processing
- All tests automated

---

**Document Version**: 1.0
**Created**: February 20, 2026
**Status**: Ready for Execution
**Next Step**: Begin Task 1.1 - Fix Unit Tests

---

*"Test-first development is not about testing; it's about design. Writing tests before code forces you to think about the problem, not just hack a solution."* - Unknown
