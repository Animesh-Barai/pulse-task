from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.models import TaskList
from app.services.socket_helpers import handle_ydoc_update, simple_socket_manager


async def create_ydoc(
    workspace_id: str,
    title: str,
    db: AsyncIOMotorDatabase
) -> TaskList:
    """
    Create a new Yjs document (list) and generate a unique key.
    """
    import uuid
    import hashlib

    y_doc_key = hashlib.sha256(f"{workspace_id}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]

    ydoc_dict = {
        "workspace_id": workspace_id,
        "title": title,
        "y_doc_key": y_doc_key,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = await db.ydocs.insert_one(ydoc_dict)

    return TaskList(
        id=str(result.inserted_id),
        workspace_id=workspace_id,
        title=title,
        y_doc_key=y_doc_key,
        created_at=ydoc_dict["created_at"]
    )


async def get_ydoc(y_doc_key: str, db: AsyncIOMotorDatabase) -> Optional[TaskList]:
    """
    Get a Yjs document by its unique key.
    """
    ydoc_dict = await db.ydocs.find_one({"y_doc_key": y_doc_key})
    if ydoc_dict:
        ydoc_dict["id"] = str(ydoc_dict["_id"])
        return TaskList(**ydoc_dict)
    return None


async def update_ydoc_snapshot(
    y_doc_key: str,
    snapshot_data: dict,
    snapshot_metadata: dict,
    db: AsyncIOMotorDatabase
) -> bool:
    """
    Update the Yjs document snapshot in MongoDB.
    """
    update_dict = {
        "yjs_state": snapshot_data.get("yjs_state"),
        "snapshot_metadata": snapshot_metadata,
        "updated_at": datetime.utcnow()
    }

    result = await db.ydocs.update_one(
        {"y_doc_key": y_doc_key},
        {"$set": update_dict}
    )

    return result.modified_count > 0


async def delete_ydoc(y_doc_key: str, db: AsyncIOMotorDatabase) -> bool:
    """
    Delete a Yjs document from database.
    """
    result = await db.ydocs.delete_one({"y_doc_key": y_doc_key})
    return result.deleted_count > 0


async def list_ydocs_by_workspace(
    workspace_id: str,
    db: AsyncIOMotorDatabase
) -> List[TaskList]:
    """
    List all Yjs documents belonging to a workspace.
    """
    cursor = db.ydocs.find({"workspace_id": workspace_id})
    ydocs = await cursor.to_list(length=100)

    return [TaskList(**doc) for doc in ydocs]


async def apply_crdt_operations(
    ydoc_key: str,
    operations: List[dict],
    db: AsyncIOMotorDatabase
) -> bool:
    """
    Apply queued CRDT operations to Yjs document in database.
    """
    try:
        from app.services.crdt_service import get_ydoc

        # Get current state
        ydoc = await get_ydoc(ydoc_key, db)
        if not ydoc:
            return False

        # Parse current state (in real app, would use ypy library)
        # For now, we simulate applying operations to state
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

    except Exception as e:
        return False
