from typing import List, Optional
import json
from datetime import datetime, timedelta
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorDatabase


async def queue_offline_operations(
    user_id: str,
    ydoc_key: str,
    operations: List[dict],
    redis_client: redis.Redis
) -> str:
    """
    Queue CRDT operations for offline user.
    Operations will be synced when user reconnects.
    """
    queue_data = {
        "user_id": user_id,
        "ydoc_key": ydoc_key,
        "operations": operations,
        "queued_at": datetime.utcnow().isoformat()
    }

    key = f"offline_ops:{user_id}:{ydoc_key}"
    await redis_client.lpush(key, json.dumps(queue_data))

    # Set expiry to 24 hours (operations expire if not synced)
    await redis_client.expire(key, 86400)

    return key


async def get_queued_operations(
    user_id: str,
    ydoc_key: str,
    redis_client: redis.Redis
) -> List[dict]:
    """
    Get all queued CRDT operations for a specific Yjs document.
    """
    key = f"offline_ops:{user_id}:{ydoc_key}"
    operations_data = await redis_client.lrange(key, 0, -1)

    queued_ops = []
    for op_data in operations_data:
        queued_ops.append(json.loads(op_data))

    return queued_ops


async def clear_queued_operations(
    user_id: str,
    ydoc_key: str,
    redis_client: redis.Redis
) -> bool:
    """
    Clear all queued operations after successful sync.
    """
    key = f"offline_ops:{user_id}:{ydoc_key}"
    result = await redis_client.delete(key)
    return result > 0


async def mark_operations_as_synced(
    user_id: str,
    ydoc_key: str,
    operation_ids: List[str],
    redis_client: redis.Redis
) -> None:
    """
    Mark specific operations as synced (optional for tracking).
    """
    key = f"offline_ops:{user_id}:{ydoc_key}"

    # Get all queued operations
    all_ops = await redis_client.lrange(key, 0, -1)

    # Filter out synced operations
    remaining_ops = []
    for op_data in all_ops:
        op = json.loads(op_data)
        if op.get("op_id") not in operation_ids:
            remaining_ops.append(op_data)

    # Remove all and re-add remaining
    await redis_client.delete(key)
    for op in remaining_ops:
        await redis_client.lpush(key, op)


async def get_all_user_offline_ops(
    user_id: str,
    redis_client: redis.Redis
) -> dict[str, List[dict]]:
    """
    Get all offline operations for a user, organized by Yjs document.
    Returns: {"ydoc_key": [operations]}
    """
    pattern = f"offline_ops:{user_id}:*"
    keys = await redis_client.keys(pattern)

    all_ops = {}
    for key in keys:
        ydoc_key = key.split(":")[-1]
        operations_data = await redis_client.lrange(key, 0, -1)
        ops = [json.loads(op) for op in operations_data]
        all_ops[ydoc_key] = ops

    return all_ops


async def apply_crdt_operations(
    ydoc_key: str,
    operations: List[dict],
    db: AsyncIOMotorDatabase
) -> bool:
    """
    Apply queued CRDT operations to the Yjs document in database.
    Updates the Yjs state with operations applied while user was offline.
    """
    try:
        from app.services.crdt_service import update_ydoc_snapshot

        # Get current state
        ydoc = await get_ydoc(ydoc_key, db)
        if not ydoc:
            return False

        # Parse current state (in real app, would use ypy library)
        # For now, we'll simulate state updates
        current_state = ydoc.get("yjs_state", {})

        # Apply operations sequentially (CRDT property ensures consistency)
        for operation in operations:
            op_type = operation.get("type")
            position = operation.get("position")

            if op_type == "insert":
                current_state[f"pos_{position}"] = operation.get("text")
            elif op_type == "delete":
                current_state.pop(f"pos_{position}", None)
            elif op_type == "update":
                current_state[f"pos_{position}"] = operation.get("text")

        # Save updated state
        snapshot_metadata = {
            "operations_applied": len(operations),
            "applied_at": datetime.utcnow().isoformat(),
            "compressed": True
        }

        await update_ydoc_snapshot(
            ydoc_key,
            {"yjs_state": current_state},
            snapshot_metadata,
            db
        )

        return True

    except Exception:
        return False
