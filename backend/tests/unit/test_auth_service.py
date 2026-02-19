import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import (
    create_user,
    get_user_by_email,
    authenticate_user,
    create_refresh_token_in_db,
    revoke_refresh_token,
    is_refresh_token_valid
)
from app.models.models import UserCreate, UserInDB
from datetime import datetime


@pytest.mark.asyncio
class TestAuthService:
    async def test_create_user_success(self):
        """Test creating a new user successfully."""
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password="securepassword123"
        )

        mock_db = MagicMock()
        mock_insert = AsyncMock()
        mock_insert.return_value = MagicMock(inserted_id="user_123")
        mock_db.users.insert_one = mock_insert

        result = await create_user(user_data, mock_db)

        assert result is not None
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        mock_insert.assert_called_once()

    async def test_create_user_hashes_password(self):
        """Test that password is hashed when creating user."""
        from app.core.security import get_password_hash

        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password="securepassword123"
        )

        mock_db = MagicMock()
        mock_insert = AsyncMock()
        mock_insert.return_value = MagicMock(inserted_id="user_123")
        mock_db.users.insert_one = mock_insert

        await create_user(user_data, mock_db)

        # Verify password was hashed
        call_args = mock_insert.call_args[0][0]
        assert call_args["password_hash"] != "securepassword123"
        assert len(call_args["password_hash"]) > 50

    async def test_get_user_by_email_exists(self):
        """Test getting user that exists."""
        user_dict = {
            "_id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "password_hash": "hashed_password",
            "created_at": datetime.utcnow()
        }

        mock_db = MagicMock()
        mock_find_one = AsyncMock()
        mock_find_one.return_value = user_dict
        mock_db.users.find_one = mock_find_one

        result = await get_user_by_email("test@example.com", mock_db)

        assert result is not None
        assert result.email == "test@example.com"
        assert result.name == "Test User"

    async def test_get_user_by_email_not_exists(self):
        """Test getting user that doesn't exist."""
        mock_db = MagicMock()
        mock_find_one = AsyncMock()
        mock_find_one.return_value = None
        mock_db.users.find_one = mock_find_one

        result = await get_user_by_email("nonexistent@example.com", mock_db)

        assert result is None

    async def test_authenticate_user_success(self):
        """Test authenticating user with correct credentials."""
        from app.core.security import get_password_hash
        password_hash = get_password_hash("securepassword123")

        user_dict = {
            "_id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        }

        mock_db = MagicMock()

        with patch('app.services.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = UserInDB(**user_dict)

            result = await authenticate_user("test@example.com", "securepassword123", mock_db)

            assert result is not None
            assert result.email == "test@example.com"

    async def test_authenticate_user_wrong_password(self):
        """Test authenticating user with wrong password returns None."""
        from app.core.security import get_password_hash
        password_hash = get_password_hash("correctpassword")

        user_dict = {
            "_id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        }

        mock_db = MagicMock()

        with patch('app.services.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = UserInDB(**user_dict)

            result = await authenticate_user("test@example.com", "wrongpassword", mock_db)

            assert result is None

    async def test_authenticate_user_not_exists(self):
        """Test authenticating non-existent user returns None."""
        mock_db = MagicMock()

        with patch('app.services.auth_service.get_user_by_email', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await authenticate_user("nonexistent@example.com", "password", mock_db)

            assert result is None

    async def test_create_refresh_token_in_db(self):
        """Test storing refresh token in database."""
        mock_db = MagicMock()
        mock_insert = AsyncMock()
        mock_insert.return_value = MagicMock(inserted_id="token_123")
        mock_db.refresh_tokens.insert_one = mock_insert

        await create_refresh_token_in_db("user_123", "refresh_token_value", mock_db)

        mock_insert.assert_called_once()
        call_args = mock_insert.call_args[0][0]
        assert call_args["user_id"] == "user_123"
        assert call_args["token"] == "refresh_token_value"

    async def test_revoke_refresh_token(self):
        """Test revoking a refresh token."""
        mock_db = MagicMock()
        mock_update_one = AsyncMock()
        mock_update_one.return_value = MagicMock(modified_count=1)
        mock_db.refresh_tokens.update_one = mock_update_one

        await revoke_refresh_token("refresh_token_value", mock_db)

        mock_update_one.assert_called_once()

    async def test_is_refresh_token_valid_true(self):
        """Test checking if refresh token is valid (not revoked)."""
        mock_db = MagicMock()
        mock_find_one = AsyncMock()
        mock_find_one.return_value = {
            "_id": "token_123",
            "user_id": "user_123",
            "token": "refresh_token_value",
            "revoked": False,
            "expires_at": datetime.utcnow()
        }
        mock_db.refresh_tokens.find_one = mock_find_one

        result = await is_refresh_token_valid("refresh_token_value", mock_db)

        assert result is True

    async def test_is_refresh_token_valid_false_revoked(self):
        """Test checking if revoked token is invalid."""
        mock_db = MagicMock()
        mock_find_one = AsyncMock()
        mock_find_one.return_value = {
            "_id": "token_123",
            "user_id": "user_123",
            "token": "refresh_token_value",
            "revoked": True,
            "expires_at": datetime.utcnow()
        }
        mock_db.refresh_tokens.find_one = mock_find_one

        result = await is_refresh_token_valid("refresh_token_value", mock_db)

        assert result is False

    async def test_is_refresh_token_valid_false_not_exists(self):
        """Test checking if non-existent token is invalid."""
        mock_db = MagicMock()
        mock_find_one = AsyncMock()
        mock_find_one.return_value = None
        mock_db.refresh_tokens.find_one = mock_find_one

        result = await is_refresh_token_valid("nonexistent_token", mock_db)

        assert result is False
