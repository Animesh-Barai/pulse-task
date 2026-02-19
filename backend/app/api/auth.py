from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_refresh_token_in_db,
    revoke_refresh_token,
    is_refresh_token_valid
)
from app.api.dependencies import get_current_user, get_optional_current_user
from app.db.database import get_database
from app.core.security import (
    create_access_token,
    create_refresh_token as create_jwt_refresh_token,
    decode_token
)
from app.models.models import UserCreate, User
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user.
    Returns 201 on success, 409 if email already exists.
    """
    from app.services.auth_service import get_user_by_email

    # Check if user already exists
    existing_user = await get_user_by_email(request.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user
    user = await create_user(
        UserCreate(
            email=request.email,
            name=request.name,
            password=request.password
        ),
        db
    )

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Authenticate a user and return JWT tokens.
    Returns 401 if credentials are invalid.
    """
    # Authenticate user
    user = await authenticate_user(request.email, request.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    # Create refresh token
    refresh_token = create_jwt_refresh_token(data={"sub": user.id})

    # Store refresh token in database
    await create_refresh_token_in_db(user.id, refresh_token, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user.
    Requires valid JWT token.
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Refresh an access token using a refresh token.
    Returns 401 if refresh token is invalid or revoked.
    """
    # Validate refresh token
    token_valid = await is_refresh_token_valid(request.refresh_token, db)
    if not token_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Decode refresh token to get user ID
    payload = decode_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Create new access token
    access_token = create_access_token(data={"sub": user_id})

    # Create new refresh token
    new_refresh_token = create_jwt_refresh_token(data={"sub": user_id})

    # Store new refresh token
    await create_refresh_token_in_db(user_id, new_refresh_token, db)

    # Revoke old refresh token
    await revoke_refresh_token(request.refresh_token, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Logout a user by revoking their refresh token.
    """
    await revoke_refresh_token(request.refresh_token, db)
    return {"message": "Successfully logged out"}
