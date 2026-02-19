import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from datetime import timedelta


class TestPasswordSecurity:
    def test_get_password_hash_returns_hash(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50

    def test_verify_password_correct_password(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password("wrong_password", hashed) is False

    def test_hash_different_passwords_different_hashes(self):
        password1 = "password_one"
        password2 = "password_two"
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        assert hash1 != hash2

    def test_hash_same_password_different_hashes(self):
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2


class TestJWTSecurity:
    def test_create_access_token(self):
        data = {"sub": "test_user_id", "email": "test@example.com"}
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100

    def test_create_access_token_with_custom_expiry(self):
        data = {"sub": "test_user_id"}
        token = create_access_token(data, expires_delta=timedelta(hours=2))
        assert token is not None

    def test_create_refresh_token(self):
        data = {"sub": "test_user_id"}
        token = create_refresh_token(data)
        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        data = {"sub": "test_user_id", "email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test_user_id"
        assert decoded["email"] == "test@example.com"
        assert decoded["type"] == "access"

    def test_decode_refresh_token(self):
        data = {"sub": "test_user_id"}
        token = create_refresh_token(data)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["type"] == "refresh"

    def test_decode_invalid_token(self):
        decoded = decode_token("invalid.token.string")
        assert decoded is None

    def test_access_token_has_expiry(self):
        data = {"sub": "test_user_id"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert "exp" in decoded

    def test_refresh_token_has_expiry(self):
        data = {"sub": "test_user_id"}
        token = create_refresh_token(data)
        decoded = decode_token(token)
        assert "exp" in decoded
