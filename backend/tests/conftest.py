import pytest
from unittest.mock import MagicMock, AsyncMock

# FastAPI test app
from fastapi.testclient import TestClient
from app.test_app import app


@pytest.fixture(scope="function")
def mock_current_user():
    """Mock user for authentication."""
    user = MagicMock()
    user.id = "test_user_123"
    user.email = "test@example.com"
    user.name = "Test User"
    return user


@pytest.fixture(scope="function")
def mock_database():
    """Mock database for tests."""
    db = AsyncMock()
    db.tasks = AsyncMock()
    return db


@pytest.fixture(scope="function")
def client(mock_current_user, mock_database):
    """TestClient fixture for task API tests with mocked auth and database."""
    from app.api.dependencies import get_current_user
    from app.db.database import get_database

    # Override the get_current_user dependency
    async def override_get_current_user():
        return mock_current_user

    # Override the get_database dependency
    async def override_get_database():
        return mock_database

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_database] = override_get_database

    with TestClient(app=app) as test_client:
        yield test_client

    # Clean up the overrides
    app.dependency_overrides.clear()
