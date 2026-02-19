import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.models.models import User


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_user_registration_success(self, client: AsyncClient):
        """Test successful user registration."""
        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"

        with patch('app.api.auth.create_user', return_value=mock_user):
            response = await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "test@example.com",
                    "name": "Test User",
                    "password": "securepassword123"
                }
            )

        assert response.status_code == 201
        data = response.json()
        assert "email" in data
        assert data["email"] == "test@example.com"

    async def test_user_registration_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email returns 422."""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "invalid-email",
                "name": "Test User",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 422

    async def test_user_registration_short_password(self, client: AsyncClient):
        """Test registration with short password returns 422."""
        with patch('app.api.auth.create_user', return_value=MagicMock()):
            response = await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "test@example.com",
                    "name": "Test User",
                    "password": "short"
                }
            )
        assert response.status_code == 422

    async def test_user_login_success(self, client: AsyncClient):
        """Test successful user login returns JWT tokens."""
        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_user.email = "test@example.com"

        with patch('app.api.auth.authenticate_user', return_value=mock_user):
            with patch('app.api.auth.create_refresh_token_in_db', return_value="new_refresh_token"):
                response = await client.post(
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

    async def test_user_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials returns 401."""
        with patch('app.api.auth.authenticate_user', return_value=None):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword"
                }
            )

        assert response.status_code == 401

    async def test_get_current_user_with_valid_token(self, client: AsyncClient):
        """Test getting current user with valid token."""
        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user_dict = {
            "id": "user_123",
            "email": "test@example.com",
            "name": "Test User"
        }

        with patch('app.api.dependencies.get_current_user', return_value=mock_user):
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer valid_token"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data == mock_user_dict

    async def test_refresh_token_success(self, client: AsyncClient):
        """Test refreshing access token."""
        mock_response = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer"
        }

        with patch('app.api.auth.create_access_token', return_value="new_access_token"):
            with patch('app.api.auth.create_refresh_token', return_value="new_refresh_token"):
                with patch('app.api.auth.is_refresh_token_valid', return_value=True):
                    with patch('app.api.auth.decode_token', return_value={"sub": "user_123"}):
                        with patch('app.api.auth.create_refresh_token_in_db', return_value="new_refresh_token"):
                            with patch('app.api.auth.revoke_refresh_token', return_value=True):
                                response = await client.post(
                                    "/api/v1/auth/refresh",
                                    json={"refresh_token": "valid_token"}
                                )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_logout_success(self, client: AsyncClient):
        """Test successful logout."""
        with patch('app.api.auth.revoke_refresh_token', return_value=True):
            response = await client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "refresh_token_value"}
            )

        assert response.status_code == 200
