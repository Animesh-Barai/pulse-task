from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings

client: Optional[AsyncIOMotorClient] = None
database = None


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
