from typing import List, Dict, Any
import json
import asyncio


async def update_user_presence(
    user_id: str,
    workspace_id: str,
    presence: str,
    redis_client=None
):
    """
    Update user presence in workspace (online/offline/away).
    Uses Redis for real-time presence tracking.
    """
    if redis_client:
        presence_key = f"presence:{workspace_id}:{user_id}"
        await redis_client.setex(
            presence_key,
            300,  # 5 minutes TTL
            json.dumps({
                "user_id": user_id,
                "presence": presence,
                "timestamp": asyncio.get_event_loop().time()
            })
        )


async def get_workspace_users(
    workspace_id: str,
    redis_client=None
) -> List[Dict[str, Any]]:
    """
    Get all users with presence status in workspace.
    """
    if redis_client:
        pattern = f"presence:{workspace_id}:*"
        keys = await redis_client.keys(pattern)
        users = []
        for key in keys:
            data = await redis_client.get(key)
            if data:
                users.append(json.loads(data))
        return users
    return []


async def remove_user_presence(
    user_id: str,
    workspace_id: str,
    redis_client=None
) -> bool:
    """
    Remove user presence from workspace.
    """
    if redis_client:
        presence_key = f"presence:{workspace_id}:{user_id}"
        await redis_client.delete(presence_key)
        return True
    return False
