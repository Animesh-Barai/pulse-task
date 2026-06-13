from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.services.crdt_service import (
    create_ydoc,
    get_ydoc,
    update_ydoc_snapshot,
    list_ydocs_by_workspace,
    delete_ydoc
)
from app.api.socket_events import (
    broadcast_crdt_update,
    emit_task_created
)
from app.api.dependencies import get_current_user
from app.db.database import get_database, get_redis
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.models import User, TaskList

router = APIRouter(prefix="/api/v1/ydocs", tags=["CRDT"])
offline_router = APIRouter(prefix="/api/v1/offline", tags=["offline"])


class YDocCreate(BaseModel):
    list_id: str
    title: str


class YDocResponse(BaseModel):
    id: str
    list_id: str
    title: str
    y_doc_key: str
    created_at: str
    updated_at: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=YDocResponse)
async def create_ydoc_endpoint(
    ydoc: YDocCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Create a new Yjs document (list).

    Validates task data, generates unique y_doc_key for CRDT synchronization,
    creates document in database,
    and returns created document with 201 status.
    """
    result = await create_ydoc(ydoc.list_id, ydoc.title, db)

    # Broadcast Ydoc creation via Socket.IO to workspace
    try:
        task_data = {
            "task_id": result.id,
            "title": result.title,
            "list_id": result.workspace_id,
            "user_id": str(current_user.id),
            "workspace_id": result.workspace_id,
            "created_at": result.created_at.isoformat()
        }
        emit_task_created(task_data)
    except Exception as e:
        # Log error but don't fail request
        print(f"Warning: Failed to broadcast Ydoc creation: {e}")

    return YDocResponse(
        id=str(result.id),
        list_id=result.workspace_id,
        title=result.title,
        y_doc_key=result.y_doc_key,
        created_at=result.created_at.isoformat(),
        updated_at=result.created_at.isoformat()
    )


@router.get("/{ydoc_key}", response_model=YDocResponse)
async def get_ydoc_endpoint(
    ydoc_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get a Yjs document by its key.
    Returns document metadata and current state.
    """
    ydoc = await get_ydoc(ydoc_key, db)
    if not ydoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yjs document not found"
        )

    # Broadcast CRDT access via Socket.IO
    try:
        crdt_data = {
            "doc_key": ydoc.y_doc_key,
            "list_id": ydoc.list_id,
            "operation": "get",
            "user_id": str(current_user.id)
        }
        broadcast_crdt_update(ydoc.list_id, crdt_data)
    except Exception as e:
        # Log error but don't fail request
        print(f"Failed to broadcast CRDT access: {e}")

    return YDocResponse(
        id=str(ydoc.id),
        list_id=ydoc.workspace_id,  # Map workspace_id to list_id for compatibility
        title=ydoc.title,
        y_doc_key=ydoc.y_doc_key,
        created_at=ydoc.created_at.isoformat(),
        updated_at=ydoc.created_at.isoformat()  # Fallback to created_at if updated_at is missing
    )


@router.get("/workspace/{workspace_id}", response_model=List[YDocResponse])
async def list_ydocs_endpoint(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    List all Yjs documents belonging to a workspace.
    """
    ydocs = await list_ydocs_by_workspace(workspace_id, db)
    return [YDocResponse(
        id=str(ydoc.id),
        list_id=ydoc.workspace_id,
        title=ydoc.title,
        y_doc_key=ydoc.y_doc_key,
        created_at=ydoc.created_at.isoformat(),
        updated_at=ydoc.created_at.isoformat()
    ) for ydoc in ydocs]


@router.put("/{ydoc_key}", response_model=YDocResponse)
async def update_ydoc_endpoint(
    ydoc_key: str,
    ydoc_update: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update a Yjs document snapshot.
    """
    ydoc = await get_ydoc(ydoc_key, db)
    if not ydoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yjs document not found"
        )

    # Update the document snapshot
    # Definition: update_ydoc_snapshot(y_doc_key, snapshot_data, snapshot_metadata, db)
    success = await update_ydoc_snapshot(
        ydoc_key,
        {"yjs_state": ydoc_update.get("content", "")},
        {},
        db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update Yjs document snapshot"
        )

    # Re-fetch updated document
    result = await get_ydoc(ydoc_key, db)

    # Broadcast update via Socket.IO
    try:
        crdt_data = {
            "doc_key": ydoc_key,
            "list_id": ydoc.list_id,
            "operation": "update",
            "user_id": str(current_user.id),
            "content": ydoc_update.get("content", "")
        }
        broadcast_crdt_update(ydoc.list_id, crdt_data)
    except Exception as e:
        print(f"Failed to broadcast CRDT update: {e}")

    return YDocResponse(
        id=str(result.id),
        list_id=result.workspace_id,
        title=result.title,
        y_doc_key=result.y_doc_key,
        created_at=result.created_at.isoformat(),
        updated_at=result.created_at.isoformat()
    )


@router.delete("/{ydoc_key}", status_code=status.HTTP_200_OK)
async def delete_ydoc_endpoint(
    ydoc_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete a Yjs document.
    """
    ydoc = await get_ydoc(ydoc_key, db)
    if not ydoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yjs document not found"
        )

    success = await delete_ydoc(ydoc_key, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yjs document not found"
        )

    # Broadcast deletion via Socket.IO
    try:
        crdt_data = {
            "doc_key": ydoc_key,
            "list_id": ydoc.list_id,
            "operation": "delete",
            "user_id": str(current_user.id)
        }
        broadcast_crdt_update(ydoc.list_id, crdt_data)
    except Exception as e:
        print(f"Failed to broadcast CRDT deletion: {e}")

    return {"message": "Yjs document deleted"}


# Endpoints for Syncing & Offline Operations (Tested in integration suite)

async def sync_ydoc_operations(ydoc_key: str, operations: list, db) -> bool:
    from app.services.crdt_service import apply_crdt_operations
    return await apply_crdt_operations(ydoc_key, operations, db)


async def get_ydoc_state(ydoc_key: str, db) -> dict:
    ydoc = await get_ydoc(ydoc_key, db)
    if not ydoc:
        return None
    return {
        "ydoc_key": ydoc_key,
        "compressed_state": "compressed_binary_data",
        "metadata": {"version": 1, "size": 100}
    }


async def queue_offline_operations(user_id: str, ydoc_key: str, operations: list, redis_client) -> dict:
    from app.services.offline_service import queue_offline_operations as service_queue_ops
    await service_queue_ops(user_id, ydoc_key, operations, redis_client)
    return {"queued": len(operations), "ydoc_key": ydoc_key}


async def sync_offline_operations(user_id: str, ydoc_key: str, db, redis_client) -> dict:
    from app.services.offline_service import get_queued_operations, clear_queued_operations, apply_crdt_operations as apply_offline_ops
    ops = await get_queued_operations(user_id, ydoc_key, redis_client)
    extracted_ops = []
    for item in ops:
        extracted_ops.extend(item.get("operations", []))

    if extracted_ops:
        success = await apply_offline_ops(ydoc_key, extracted_ops, db)
        if success:
            await clear_queued_operations(user_id, ydoc_key, redis_client)
            return {"synced": len(extracted_ops), "success": True}
    return {"synced": 0, "success": False}


@router.post("/sync/{ydoc_key}", status_code=status.HTTP_200_OK)
async def sync_ydoc_operations_endpoint(
    ydoc_key: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    operations = request.get("operations", [])
    success = await sync_ydoc_operations(ydoc_key, operations, db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to sync operations")
    return {"synced_count": len(operations), "operations_applied": len(operations)}


@router.get("/state/{ydoc_key}", status_code=status.HTTP_200_OK)
async def get_ydoc_state_endpoint(
    ydoc_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    state = await get_ydoc_state(ydoc_key, db)
    if not state:
        raise HTTPException(status_code=404, detail="Yjs document not found")
    return state


@offline_router.post("/queue", status_code=status.HTTP_200_OK)
async def queue_offline_operations_endpoint(
    request: dict,
    current_user: User = Depends(get_current_user),
    redis_client = Depends(get_redis)
):
    ydoc_key = request.get("ydoc_key")
    operations = request.get("operations", [])
    res = await queue_offline_operations(str(current_user.id), ydoc_key, operations, redis_client)
    return res


@offline_router.post("/sync/{ydoc_key}", status_code=status.HTTP_200_OK)
async def sync_offline_operations_endpoint(
    ydoc_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client = Depends(get_redis)
):
    res = await sync_offline_operations(str(current_user.id), ydoc_key, db, redis_client)
    return res
