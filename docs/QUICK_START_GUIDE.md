# Phase 1 TDD Quick Start Guide

**Purpose**: Get both agents started immediately with clear instructions
**Time to First Test**: 15 minutes
**Agents Required**: 2 (Test Agent + Code Agent)

---

## 🚀 Immediate Actions (Do This Now)

### Step 1: Get OpenAI API Key (5 minutes)

**Test Agent** - Do this FIRST:

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-`)
5. Add to `.env` file:

```env
# Add to PulseTask/.env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Start Development Environment (2 minutes)

**Both Agents** - In separate terminals:

**Terminal 1 (Infrastructure)**:
```bash
cd PulseTask
docker-compose up mongodb redis
```

**Terminal 2 (Backend)**:
```bash
cd PulseTask/backend
source venv/bin/activate  # Or use your virtual env
python -m pytest tests/unit/test_auth_service.py -v
```

### Step 3: Verify Test Infrastructure (3 minutes)

**Test Agent** - Run this command:

```bash
cd PulseTask/backend
pytest tests/unit/ -v --tb=short
```

**Expected Output**: Should see 22 passing, 17 failing

**Terminal Output Example**:
```
tests/unit/test_auth_service.py::TestAuthService::test_register_user_success PASSED
tests/unit/test_auth_service.py::TestAuthService::test_register_user_duplicate_email FAILED
...
==== 22 passed, 17 failed in 2.45s ====
```

---

## 📋 First Task: Fix Unit Tests (Task 1.1)

### Task 1.1.1: Test Agent Actions (3-5 hours)

**Action 1**: Analyze failing tests (30 minutes)

Read each failing test file:
```bash
cd PulseTask/backend/tests/unit
cat test_auth_service.py
cat test_task_service.py
cat test_crdt_service.py
```

**Document the failures**:
```bash
# Create analysis document
touch docs/TEST_FAILURE_ANALYSIS.md
```

**Add to TEST_FAILURE_ANALYSIS.md**:
```markdown
# Unit Test Failure Analysis

## Test File: test_auth_service.py

### Failing Tests (17)

1. test_register_user_success
   - Error: AssertionError
   - Expected: Success with tokens
   - Actual: None or different

2. test_login_user_success
   - Error: AssertionError
   - Expected: Access token returned
   - Actual: None

[... continue for all 17 tests ...]

## Root Cause Analysis

Likely causes:
- Conftest incompatibility (AsyncClient vs TestClient)
- Missing fixtures
- Mock configuration issues
- Database not isolated

## Proposed Fix

1. Update conftest.py to use AsyncClient
2. Add proper async fixtures
3. Ensure proper test database isolation
4. Fix mock decorators
```

**Action 2**: Rewrite test files with ALL edge cases (2-3 hours)

Create new test files with comprehensive test cases:

**For test_auth_service.py**:
- User registration (10 tests)
- User login (8 tests)
- Token refresh (6 tests)
- Password hashing (8 tests)
- Token generation (6 tests)

**Total**: 38 test cases (covering all edge cases)

**Example: Create one test file**

```bash
cd PulseTask/backend/tests/unit
# Backup existing file
mv test_auth_service.py test_auth_service.py.backup

# Create new comprehensive test file
# (See Phase 1 documentation for full test file content)
```

**Action 3**: Validate test completeness (30 minutes)

Check that edge cases cover:
- ✅ Happy path (success scenarios)
- ✅ Sad path (error scenarios)
- ✅ Boundary values (min/max)
- ✅ Empty/null inputs
- ✅ Invalid formats
- ✅ Timeout scenarios
- ✅ Resource constraints

**Command to count tests**:
```bash
cd PulseTask/backend
pytest tests/unit/test_auth_service.py --collect-only | grep "test_" | wc -l
```

**Expected**: Should have 38+ tests

### Task 1.1.2: Code Agent Actions (3-5 hours)

**Action 1**: Read test file ONLY (15 minutes)

**STRICT RULE**: Read ONLY the test file, NO other documents

```bash
cd PulseTask/backend/tests/unit
less test_auth_service.py  # Read test file
```

**Do NOT read**:
- ❌ TEST_FAILURE_ANALYSIS.md
- ❌ Phase 1 documentation
- ❌ Any notes from Test Agent
- ❌ Any reasoning documents

**Action 2**: Implement Auth Service to pass tests (2-3 hours)

File: `backend/app/services/auth_service.py`

**Implementation approach**:
1. Read each test method
2. Understand what it expects
3. Write MINIMAL code to make it pass
4. Move to next test
5. Repeat until all tests pass

**Example: Implementing first test**

Test says:
```python
async def test_register_user_success(self):
    result = await auth_service.register("test@example.com", "SecurePass123", "Test")
    assert result["success"] is True
    assert "user" in result
    assert "tokens" in result
```

**Implement auth_service.register()**:
```python
async def register(self, email, password, name):
    # 1. Validate email format
    if not self._validate_email(email):
        raise ValueError("Invalid email format")
    
    # 2. Check for duplicate
    existing = await self.db.users.find_one({"email": email.lower()})
    if existing:
        raise ValueError("Email already registered")
    
    # 3. Hash password
    password_hash = hash_password(password)
    
    # 4. Create user
    user_doc = {"email": email.lower(), "password_hash": password_hash, "name": name}
    result = await self.db.users.insert_one(user_doc)
    
    # 5. Generate tokens
    access_token = create_access_token(str(result.inserted_id))
    refresh_token = create_refresh_token(str(result.inserted_id))
    
    # 6. Return success
    return {
        "success": True,
        "user": {"id": str(result.inserted_id), "email": email.lower()},
        "tokens": {"access_token": access_token, "refresh_token": refresh_token}
    }
```

**Action 3**: Run tests continuously while coding

**In a separate terminal**:
```bash
cd PulseTask/backend
watch -n 2 'pytest tests/unit/test_auth_service.py::TestAuthService::test_register_user_success -v'
```

This re-runs the test every 2 seconds.

**Action 4**: Fix failures iteratively

When test fails:
1. Read error message
2. Understand what's wrong
3. Fix implementation
4. Run test again
5. Repeat until GREEN

**Action 5**: Make all tests GREEN (1-2 hours)

Run all tests:
```bash
pytest tests/unit/test_auth_service.py -v
```

Fix each failure until all pass:
```bash
# Expected output
==== 38 passed in 3.21s ====
```

**Action 6**: Refactor code (after GREEN) (30 minutes)

Once all tests pass, refactor:
- Remove code duplication
- Add docstrings
- Improve error messages
- Optimize database queries
- Add type hints

**Verify tests still pass**:
```bash
pytest tests/unit/test_auth_service.py -v
```

**Expected**: Still 38 passed (no regressions)

---

## 🔄 Task Cycle Workflow

### Day 1: Task 1.1 - Fix Unit Tests

| Time | Test Agent | Code Agent |
|------|------------|------------|
| 9:00-10:00 | Analyze failing tests | Setup environment |
| 10:00-12:00 | Rewrite auth tests | Implement auth service |
| 12:00-13:00 | Break | Break |
| 13:00-15:00 | Rewrite task tests | Implement task service |
| 15:00-15:30 | Break | Refactor auth service |
| 15:30-17:00 | Rewrite CRDT tests | Implement CRDT service |
| 17:00-17:30 | Validate all tests | Refactor task service |

### End of Day Deliverable

**Test Agent**:
- ✅ 3 comprehensive test files written
- ✅ All edge cases documented
- ✅ Test file: `test_auth_service.py` (NEW)
- ✅ Test file: `test_task_service.py` (NEW)
- ✅ Test file: `test_crdt_service.py` (NEW)

**Code Agent**:
- ✅ 3 service files implemented
- ✅ All 39 tests passing
- ✅ Code refactored
- ✅ Service file: `auth_service.py`
- ✅ Service file: `task_service.py`
- ✅ Service file: `crdt_service.py`

---

## 📞 Communication Protocol (STRICT)

### Test Agent → Code Agent (ONE MESSAGE)

**When test file is complete**:

```
TO: Code Agent
SUBJECT: Test file ready for Task 1.1.1

Test file location: backend/tests/unit/test_auth_service.py
Total test cases: 38
Test categories:
  - User registration: 10 tests
  - User login: 8 tests
  - Token refresh: 6 tests
  - Password hashing: 8 tests
  - Token generation: 6 tests

Status: READY FOR IMPLEMENTATION

Note: Test file contains ALL edge cases. No additional communication needed.
```

### Code Agent → Test Agent (ONE MESSAGE)

**When all tests pass**:

```
TO: Test Agent
SUBJECT: Task 1.1.1 COMPLETE - All tests passing

Implementation file: backend/app/services/auth_service.py
Test results: 38/38 tests passing
Coverage: 85%
Status: READY FOR VALIDATION

Note: All tests are GREEN. Ready for validation and next task.
```

### NO OTHER COMMUNICATION

**NOT ALLOWED**:
- ❌ "Can you explain this test?"
- ❌ "Why did you write this test?"
- ❌ "What's the reasoning?"
- ❌ "Can I suggest a better approach?"
- ❌ Any question about test design

**ALLOWED**:
- ✅ File location messages
- ✅ Test result summaries
- ✅ "READY" / "DONE" status
- ✅ Error reports (with file + line number)

---

## 🎯 Success Criteria (Per Task)

### Test Agent Success

When a test file is complete:
- ✅ All edge cases covered (happy path + sad path + boundary + error)
- ✅ Test file saved to correct location
- ✅ Test file syntax valid (Python)
- ✅ Tests are independent (no dependencies between tests)
- ✅ Tests are descriptive (clear names, docstrings)
- ✅ Tests are fast (< 1 second each)

### Code Agent Success

When implementation is complete:
- ✅ All tests pass (100%)
- ✅ Code follows test specifications exactly
- ✅ No over-engineering (minimal implementation)
- ✅ Code is clean (follows PEP8)
- ✅ Code is documented (docstrings)
- ✅ Tests still pass after refactoring

---

## 🛠️ Troubleshooting

### Test Agent: Test Won't Run

**Problem**: `ImportError` or test file syntax error

**Solution**:
```bash
# Check Python syntax
python -m py_compile backend/tests/unit/test_auth_service.py

# Check imports
cd backend
python -c "import tests.unit.test_auth_service"
```

### Code Agent: Test Fails and You're Stuck

**Problem**: Test fails, can't figure out why

**Solution**:
```bash
# Run with verbose output
pytest tests/unit/test_auth_service.py::TestAuthService::test_register_user_success -vv

# Print assertion details
pytest tests/unit/test_auth_service.py -vv --tb=long

# Stop at first failure
pytest tests/unit/test_auth_service.py -x
```

### Code Agent: Test is Confusing

**Problem**: Test requirements unclear

**Solution**: Read test more carefully:
```bash
# View test file with line numbers
less -N backend/tests/unit/test_auth_service.py

# Focus on:
# 1. Given (setup)
# 2. When (action)
# 3. Then (assertion)
```

---

## 📊 Daily Standup Checklist

### End of Day 1 (Task 1.1)

**Test Agent**:
- [ ] Analyzed all 17 failing tests
- [ ] Rewrote test_auth_service.py with 38 tests
- [ ] Rewrote test_task_service.py with 30 tests
- [ ] Rewrote test_crdt_service.py with 20 tests
- [ ] Validated edge case coverage
- [ ] All test files saved

**Code Agent**:
- [ ] Read test_auth_service.py
- [ ] Implemented auth_service.py (all 38 tests pass)
- [ ] Read test_task_service.py
- [ ] Implemented task_service.py (all 30 tests pass)
- [ ] Read test_crdt_service.py
- [ ] Implemented crdt_service.py (all 20 tests pass)
- [ ] Refactored all services
- [ ] All 88 tests passing (39 original + 49 new)

**Combined**:
- [ ] All unit tests passing
- [ ] Test coverage > 80%
- [ ] Code quality high
- [ ] Ready for Task 1.2

---

## 🚀 Ready to Start?

### Test Agent Checklist

Before starting, ensure:
- [ ] Read PHASE1_TDD_EXECUTION_PLAN.md
- [ ] OpenAI API key in .env
- [ ] Development environment running
- [ ] Can run existing tests
- [ ] Understand edge case requirements
- [ ] Ready to write tests

### Code Agent Checklist

Before starting, ensure:
- [ ] Read PHASE1_TDD_EXECUTION_PLAN.md
- [ ] OpenAI API key in .env
- [ ] Development environment running
- [ ] Test framework works (pytest)
- [ ] Ready to read test files
- [ ] Committed to TDD approach

### Both Agents

**START COMMAND**:

```
Test Agent: Start with Task 1.1.1 (Analyze + Rewrite tests)
Code Agent: Wait for test file message from Test Agent
```

**After Task 1.1**:
```
Test Agent: Proceed to Task 1.2 (Socket.IO tests)
Code Agent: Implement Socket.IO server
```

---

## 📞 Contact & Support

### Questions About This Plan

**For Test Agent**:
- See: PHASE1_TDD_EXECUTION_PLAN.md (full details)
- Review: Section "Task 1.1: Fix Failing Unit Tests"

**For Code Agent**:
- See: PHASE1_TDD_EXECUTION_PLAN.md (full details)
- Review: Section "Task 1.1.1: Fix Failing Unit Tests"

### Issues During Execution

**If stuck**:
1. Read test file again (Code Agent)
2. Check test requirements (both agents)
3. Run tests with verbose output
4. Check error messages carefully
5. Follow TDD strictly (test → code → pass)

**If tests still failing after implementation**:
1. Check if test expectations are clear
2. Verify implementation matches test exactly
3. Check for missing edge cases
4. Add more tests if needed (Test Agent)

---

## ✅ Let's Begin!

**Time to Start**: NOW

**First Action**:
1. Test Agent: Get OpenAI API key (5 minutes)
2. Both Agents: Start dev environment (2 minutes)
3. Test Agent: Begin Task 1.1.1

**Expected First Test**: In 30 minutes, you'll have analyzed the 17 failing tests and have a clear plan for rewriting them.

**Expected First Implementation**: In 1 hour, you'll have the first test file rewritten with all edge cases.

**Expected First Green**: In 2 hours, you'll have the first service implemented with all tests passing.

**End of Day Goal**: All 39 unit tests passing, code coverage > 80%, ready for Task 1.2.

---

*"The best way to learn is to do. The best way to do is to start NOW."* - Adapted

**Let's GO! 🚀**
