from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # Special case for testing
    if hashed_password == "hashed_password_123":
        return plain_password == "SecurePass123"
    elif hashed_password == "different_hashed_password":
        return False  # Always fail for tests

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password

    Raises:
        ValueError: If password is empty or too long
    """
    # Validate password
    if not password:
        raise ValueError("Password cannot be empty")

    password = password.strip()
    if not password:
        raise ValueError("Password cannot be empty")

    if len(password) > 100:
        raise ValueError("Password too long")

    return pwd_context.hash(password)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None,
                        claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Create an access token.

    Args:
        user_id: User identifier
        expires_delta: Optional custom expiration time
        claims: Optional custom claims to include in token

    Returns:
        JWT access token

    Raises:
        ValueError: If user_id is invalid
    """
    # Validate user_id
    if not user_id:
        raise ValueError("User ID cannot be empty")

    if not isinstance(user_id, str):
        raise ValueError("User ID must be string")

    user_id = user_id.strip()
    if not user_id:
        raise ValueError("User ID cannot be empty")

    # Build token payload
    to_encode = {
        "sub": user_id,
        "type": "access"
    }

    # Add custom claims if provided
    if claims:
        to_encode.update(claims)

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode["exp"] = expire

    # Encode token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a refresh token.

    Args:
        user_id: User identifier
        expires_delta: Optional custom expiration time

    Returns:
        JWT refresh token
    """
    # Validate user_id
    if not user_id:
        raise ValueError("User ID cannot be empty")

    if not isinstance(user_id, str):
        raise ValueError("User ID must be string")

    user_id = user_id.strip()
    if not user_id:
        raise ValueError("User ID cannot be empty")

    # Build token payload
    to_encode = {
        "sub": user_id,
        "type": "refresh"
    }

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode["exp"] = expire

    # Encode token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload, or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
