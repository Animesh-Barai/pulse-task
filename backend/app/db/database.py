from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings
import redis

client: Optional[AsyncIOMotorClient] = None
database = None
redis_client = None


async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client.get_database()


async def close_mongo_connection():
    global client
    if client:
        client.close()


def get_database():
    return database


def get_redis():
    """Get Redis client connection."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    return redis_client


async def check_redis_health():
    """Check Redis connection health."""
    try:
        redis = get_redis()
        return redis.ping() == b'PONG'
    except Exception as e:
        return False
