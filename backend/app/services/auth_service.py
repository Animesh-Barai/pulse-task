from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.models import UserCreate, UserInDB, User
from app.core.security import get_password_hash, verify_password


async def create_user(user_data: UserCreate, db: AsyncIOMotorDatabase) -> User:
    """
    Create a new user in the database.
    Password is hashed before storing.
    """
    # Hash the password
    password_hash = get_password_hash(user_data.password)

    # Prepare user document
    user_dict = {
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }

    # Insert into database
    result = await db.users.insert_one(user_dict)

    # Return User model (without password hash)
    return User(
        id=str(result.inserted_id),
        email=user_data.email,
        name=user_data.name,
        created_at=user_dict["created_at"]
    )


async def get_user_by_email(email: str, db: AsyncIOMotorDatabase) -> Optional[UserInDB]:
    """
    Get a user by email address.
    Returns UserInDB which includes password hash for authentication.
    """
    user_dict = await db.users.find_one({"email": email})
    if user_dict:
        user_dict["id"] = str(user_dict["_id"])
        return UserInDB(**user_dict)
    return None


async def get_user_by_id(user_id: str, db: AsyncIOMotorDatabase) -> Optional[User]:
    """
    Get a user by ID.
    Returns User model (without password hash).
    """
    from bson.objectid import ObjectId

    try:
        user_dict = await db.users.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            return User(**user_dict)
    except Exception:
        pass
    return None


async def authenticate_user(email: str, password: str, db: AsyncIOMotorDatabase) -> Optional[UserInDB]:
    """
    Authenticate a user with email and password.
    Returns UserInDB if credentials are valid, None otherwise.
    """
    user = await get_user_by_email(email, db)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


async def create_refresh_token_in_db(
    user_id: str,
    token: str,
    db: AsyncIOMotorDatabase
) -> str:
    """
    Store a refresh token in the database.
    """
    from datetime import datetime, timedelta

    token_dict = {
        "user_id": user_id,
        "token": token,
        "revoked": False,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=7)
    }

    result = await db.refresh_tokens.insert_one(token_dict)
    return str(result.inserted_id)


async def revoke_refresh_token(token: str, db: AsyncIOMotorDatabase) -> bool:
    """
    Revoke a refresh token by marking it as revoked.
    """
    result = await db.refresh_tokens.update_one(
        {"token": token},
        {"$set": {"revoked": True}}
    )
    return result.modified_count > 0


async def is_refresh_token_valid(token: str, db: AsyncIOMotorDatabase) -> bool:
    """
    Check if a refresh token is valid (not revoked and not expired).
    """
    from datetime import datetime

    token_doc = await db.refresh_tokens.find_one({"token": token})

    if not token_doc:
        return False

    if token_doc.get("revoked", False):
        return False

    if token_doc.get("expires_at", datetime.min) < datetime.utcnow():
        return False

    return True
