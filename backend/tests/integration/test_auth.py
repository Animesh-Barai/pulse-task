import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.models.models import User


class TestAuthEndpoints:
    def test_user_registration_success(self, client: TestClient):
        """Test successful user registration."""
        mock_response = {
            "success": True,
            "user": {
                "id": "user_123",
                "email": "test@example.com",
                "name": "Test User"
            },
            "tokens": {
                "access_token": "mock_access_token",
                "refresh_token": "mock_refresh_token"
            }
        }

        with patch('app.services.auth_service.AuthService.register', return_value=mock_response):
            response = client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "test@example.com",
                    "name": "Test User",
                    "password": "securepassword123"
                }
            )

        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"

    def test_user_registration_invalid_email(self, client: TestClient):
        """Test registration with invalid email returns 422."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "invalid-email",
                "name": "Test User",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 422

    def test_user_registration_short_password(self, client: TestClient):
        """Test registration with short password returns 422."""
        with patch('app.services.auth_service.AuthService.register', return_value=MagicMock()):
            response = client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "test@example.com",
                    "name": "Test User",
                    "password": "short"
                }
            )
        assert response.status_code == 422

    def test_user_login_success(self, client: TestClient):
        """Test successful user login returns JWT tokens."""
        mock_user = User(
            id="user_123",
            email="test@example.com",
            name="Test User",
            created_at=datetime.utcnow()
        )

        with patch('app.api.auth.authenticate_user', return_value=mock_user):
            with patch('app.api.auth.create_refresh_token_in_db', return_value="new_refresh_token"):
                response = client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": "test@example.com",
                        "password": "securepassword123"
                    }
                )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_user_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials returns 401."""
        with patch('app.api.auth.authenticate_user', return_value=None):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword"
                }
            )

        assert response.status_code == 401

    def test_get_current_user_with_valid_token(self, client: TestClient):
        """Test getting current user with valid token."""
        mock_user = User(
            id="user_123",
            email="test@example.com",
            name="Test User",
            created_at=datetime.utcnow()
        )
        mock_user_dict = {
            "id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": mock_user.created_at.isoformat()
        }

        # Override dependency
        from app.api.dependencies import get_current_user
        async def override():
            return mock_user
        client.app.dependency_overrides[get_current_user] = override

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data == mock_user_dict

    def test_refresh_token_success(self, client: TestClient):
        """Test refreshing access token."""
        mock_user = User(
            id="user_123",
            email="test@example.com",
            name="Test User",
            created_at=datetime.utcnow()
        )

        with patch('app.api.auth.create_access_token', return_value="new_access_token"):
            with patch('app.api.auth.create_jwt_refresh_token', return_value="new_refresh_token"):
                with patch('app.api.auth.is_refresh_token_valid', return_value=True):
                    with patch('app.api.auth.decode_token', return_value={"sub": "user_123"}):
                        with patch('app.api.auth.create_refresh_token_in_db', return_value="new_refresh_token"):
                            with patch('app.api.auth.revoke_refresh_token', return_value=True):
                                # Mock the dependency database get_user_by_id or similar to return mock_user
                                with patch('app.services.auth_service.get_user_by_id', return_value=mock_user):
                                    response = client.post(
                                        "/api/v1/auth/refresh",
                                        json={"refresh_token": "valid_token"}
                                    )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_logout_success(self, client: TestClient):
        """Test successful logout."""
        with patch('app.api.auth.revoke_refresh_token', return_value=True):
            response = client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "refresh_token_value"}
            )

        assert response.status_code == 200
