"""
Presence Service - Redis-based real-time presence tracking

Supports:
- User presence (online, away, offline)
- Cursor position tracking
- Typing indicators
- Workspace member lists
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


async def update_user_presence(
    user_id: str,
    workspace_id: str,
    presence: str,
    user_name: str = None,
    redis_client=None
) -> bool:
    """
    Update user presence in workspace (online/offline/away).

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        presence: Presence status ('online', 'away', 'offline')
        user_name: Optional user display name
        redis_client: Redis client instance

    Returns:
        True if successful, False otherwise
    """
    try:
        if not redis_client:
            logger.warning("Redis client not provided")
            return False

        presence_key = f"presence:{workspace_id}:{user_id}"
        presence_data = {
            "user_id": user_id,
            "user_name": user_name,
            "presence": presence,
            "timestamp": asyncio.get_event_loop().time(),
            "last_seen": datetime.utcnow().isoformat()
        }

        # Set with 5 minute TTL
        await redis_client.setex(
            presence_key,
            300,
            json.dumps(presence_data)
        )

        logger.info(f"Updated presence for user {user_id}: {presence} in workspace {workspace_id}")
        return True

    except Exception as e:
        logger.error(f"Error updating presence for user {user_id}: {e}")
        return False


async def set_user_typing(
    user_id: str,
    workspace_id: str,
    is_typing: bool,
    redis_client=None
) -> bool:
    """
    Set or clear user's typing indicator.

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        is_typing: Whether user is currently typing
        redis_client: Redis client instance

    Returns:
        True if successful, False otherwise
    """
    try:
        if not redis_client:
            return False

        typing_key = f"typing:{workspace_id}:{user_id}"

        if is_typing:
            # Set typing status with 30 second TTL
            typing_data = {
                "user_id": user_id,
                "is_typing": True,
                "timestamp": asyncio.get_event_loop().time()
            }
            await redis_client.setex(typing_key, 30, json.dumps(typing_data))
        else:
            # Clear typing status
            await redis_client.delete(typing_key)

        logger.debug(f"User {user_id} typing: {is_typing} in workspace {workspace_id}")
        return True

    except Exception as e:
        logger.error(f"Error setting typing status for user {user_id}: {e}")
        return False


async def update_cursor_position(
    user_id: str,
    workspace_id: str,
    list_id: str = None,
    task_id: str = None,
    position: Dict[str, Any] = None,
    redis_client=None
) -> bool:
    """
    Update user's cursor position in workspace.

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        list_id: Optional Task list ID
        task_id: Optional Task ID
        position: Cursor position data {line, column}
        redis_client: Redis client instance

    Returns:
        True if successful, False otherwise
    """
    try:
        if not redis_client:
            return False

        cursor_key = f"cursor:{workspace_id}:{user_id}"
        cursor_data = {
            "user_id": user_id,
            "list_id": list_id,
            "task_id": task_id,
            "position": position,
            "updated_at": datetime.utcnow().isoformat()
        }

        # Set cursor position with 5 minute TTL
        await redis_client.setex(cursor_key, 300, json.dumps(cursor_data))

        logger.debug(f"Updated cursor for user {user_id} in workspace {workspace_id}")
        return True

    except Exception as e:
        logger.error(f"Error updating cursor for user {user_id}: {e}")
        return False


async def get_workspace_users(
    workspace_id: str,
    redis_client=None
) -> List[Dict[str, Any]]:
    """
    Get all users with presence status in workspace.

    Args:
        workspace_id: Workspace ID
        redis_client: Redis client instance

    Returns:
        List of user presence data
    """
    try:
        if not redis_client:
            return []

        # Get all presence keys for workspace
        pattern = f"presence:{workspace_id}:*"
        keys = await redis_client.keys(pattern)

        users = []
        for key in keys:
            data = await redis_client.get(key)
            if data:
                # Decode bytes to string first
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                presence_data = json.loads(data)
                # Add cursor position if exists
                cursor_key = f"cursor:{workspace_id}:{presence_data['user_id']}"
                cursor_data = await redis_client.get(cursor_key)

                if cursor_data:
                    # Decode cursor data if it's bytes
                    if isinstance(cursor_data, bytes):
                        cursor_data = cursor_data.decode('utf-8')
                    presence_data["cursor"] = json.loads(cursor_data)

                users.append(presence_data)

        logger.info(f"Retrieved {len(users)} users for workspace {workspace_id}")
        return users

    except Exception as e:
        logger.error(f"Error getting users for workspace {workspace_id}: {e}")
        return []


async def get_user_typing_status(
    workspace_id: str,
    user_ids: List[str],
    redis_client=None
) -> Dict[str, bool]:
    """
    Get typing status for multiple users in a workspace.

    Args:
        workspace_id: Workspace ID
        user_ids: List of user IDs to check
        redis_client: Redis client instance

    Returns:
        Dict mapping user_id -> is_typing status
    """
    try:
        if not redis_client or not user_ids:
            return {}

        typing_status = {}
        for user_id in user_ids:
            typing_key = f"typing:{workspace_id}:{user_id}"
            data = await redis_client.get(typing_key)

            if data:
                # Decode bytes to string first
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                typing_data = json.loads(data)
                typing_status[user_id] = typing_data.get("is_typing", False)
            else:
                typing_status[user_id] = False

        return typing_status

    except Exception as e:
        logger.error(f"Error getting typing status: {e}")
        return {}


async def get_cursor_positions(
    workspace_id: str,
    user_ids: List[str],
    redis_client=None
) -> Dict[str, Dict[str, Any]]:
    """
    Get cursor positions for multiple users in a workspace.

    Args:
        workspace_id: Workspace ID
        user_ids: List of user IDs to check
        redis_client: Redis client instance

    Returns:
        Dict mapping user_id -> cursor position data
    """
    try:
        if not redis_client or not user_ids:
            return {}

        cursor_positions = {}
        for user_id in user_ids:
            cursor_key = f"cursor:{workspace_id}:{user_id}"
            data = await redis_client.get(cursor_key)

            if data:
                # Decode bytes to string first
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                cursor_positions[user_id] = json.loads(data)

        return cursor_positions

    except Exception as e:
        logger.error(f"Error getting cursor positions: {e}")
        return {}


async def remove_user_presence(
    user_id: str,
    workspace_id: str,
    redis_client=None
) -> bool:
    """
    Remove user presence from workspace.

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        redis_client: Redis client instance

    Returns:
        True if successful, False otherwise
    """
    try:
        if not redis_client:
            return False

        # Remove presence
        presence_key = f"presence:{workspace_id}:{user_id}"
        await redis_client.delete(presence_key)

        # Remove cursor position
        cursor_key = f"cursor:{workspace_id}:{user_id}"
        await redis_client.delete(cursor_key)

        # Remove typing status
        typing_key = f"typing:{workspace_id}:{user_id}"
        await redis_client.delete(typing_key)

        logger.info(f"Removed presence for user {user_id} from workspace {workspace_id}")
        return True

    except Exception as e:
        logger.error(f"Error removing presence for user {user_id}: {e}")
        return False


async def cleanup_expired_presence(
    workspace_id: str,
    redis_client=None
) -> int:
    """
    Clean up expired presence entries for a workspace.
    Entries with TTL are automatically cleaned by Redis, but this can be used
    to manually clean if needed.

    Args:
        workspace_id: Workspace ID
        redis_client: Redis client instance

    Returns:
        Number of keys cleaned
    """
    try:
        if not redis_client:
            return 0

        # Get all keys for workspace
        patterns = [
            f"presence:{workspace_id}:*",
            f"cursor:{workspace_id}:*",
            f"typing:{workspace_id}:*"
        ]

        cleaned_count = 0
        for pattern in patterns:
            keys = await redis_client.keys(pattern)
            for key in keys:
                # Check if key exists (TTL not expired)
                if await redis_client.ttl(key) > 0:
                    # Key exists, don't delete (Redis handles TTL)
                    pass
                else:
                    # Key expired, clean up
                    await redis_client.delete(key)
                    cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired keys for workspace {workspace_id}")

        return cleaned_count

    except Exception as e:
        logger.error(f"Error cleaning up presence: {e}")
        return 0
