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
from app.services.presence_service import (
    get_workspace_users,
    update_user_presence,
    get_user_cursor_positions,
    update_user_cursor_position
)
from app.services.offline_service import (
    queue_offline_operations,
    get_queued_operations,
    clear_queued_operations,
    apply_crdt_operations,
    get_all_user_offline_ops
)
from app.services.socket_service import (
    broadcast_to_workspace,
    broadcast_presence_update,
    broadcast_typing_indicator,
    handle_ydoc_update
)
from app.api.dependencies import get_current_user
from app.db.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import socketio


router = APIRouter(prefix="/api/v1/ydocs", tags=["CRDT"])
sio = socketio.AsyncServer(async_mode='auto', cors_allowed_origins=["*"])


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


class PresenceUpdateRequest(BaseModel):
    workspace_id: str
    status: str  # 'online', 'away', 'offline'


class TypingIndicatorRequest(BaseModel):
    workspace_id: str
    is_typing: bool


class CursorPositionRequest(BaseModel):
    workspace_id: str
    position: dict  # {"line": 1, "column": 5}


class CRDTOperationsRequest(BaseModel):
    ydoc_key: str
    operations: List[dict]
    sync_type: str  # 'offline' or 'realtime'


class SyncOfflineRequest(BaseModel):
    ydoc_key: str


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=YDocResponse)
async def create_ydoc_endpoint(
    ydoc: YDocCreate,
    current_user = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new Yjs document (list).
    Generates unique y_doc_key for CRDT synchronization.
    """
    ydoc = await create_ydoc(ydoc.list_id, ydoc.title, db)
    return YDocResponse(
        id=ydoc["id"],
        list_id=ydoc.list_id,
        title=ydoc.title,
        y_doc_key=ydoc.y_doc_key,
        created_at=ydoc.created_at.isoformat()
    )


@router.get("/{ydoc_key}", response_model=YDocResponse)
async def get_ydoc_endpoint(
    ydoc_key: str,
    current_user = Depends(get_current_user),
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

    return YDocResponse(
        id=ydoc["id"],
        list_id=ydoc.list_id,
        title=ydoc.title,
        y_doc_key=ydoc.y_doc_key,
        created_at=ydoc.created_at.isoformat(),
        updated_at=ydoc.get("updated_at", "").isoformat() if ydoc.get("updated_at") else None
    )


@router.get("/workspace/{workspace_id}", response_model=List[YDocResponse])
async def list_ydocs_endpoint(
    workspace_id: str,
    current_user = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    List all Yjs documents belonging to a workspace.
    """
    from app.services.crdt_service import list_ydocs_by_workspace

    ydocs = await list_ydocs_by_workspace(workspace_id, db)
    return [YDocResponse(
        id=ydoc["id"],
        list_id=ydoc.list_id,
        title=ydoc.title,
        y_doc_key=ydoc.y_doc_key,
        created_at=ydoc.created_at.isoformat(),
        updated_at=ydoc.get("updated_at", "").isoformat() if ydoc.get("updated_at") else None
    ) for ydoc in ydocs]


@router.delete("/{ydoc_key}")
async def delete_ydoc_endpoint(
    ydoc_key: str,
    current_user = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete a Yjs document.
    """
    from app.services.socket_service import sio_manager

    success = await delete_ydoc(ydoc_key, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yjs document not found"
        )

    # Broadcast deletion to workspace members
    await broadcast_to_workspace(
        "ydoc_deleted",
        {"ydoc_key": ydoc_key, "deleted_by": current_user.id},
        f"workspace:{current_user.id}",  # Workspace ID (using user ID for simplicity)
        sio
    )

    return {"message": "Yjs document deleted"}


@router.post("/operations", response_model=dict)
async def sync_ydoc_operations_endpoint(
    request: CRDTOperationsRequest,
    current_user = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Sync CRDT operations to a Yjs document.
    Handles both realtime and offline (queued) operations.
    """
    if request.sync_type == "offline":
        # Apply offline operations
        success = await apply_crdt_operations(
            request.ydoc_key,
            request.operations,
            db
        )

        if success:
            # Clear queued operations after successful sync
            from app.services.offline_service import get_queued_operations
            await clear_queued_operations(current_user.id, request.ydoc_key, sio_manager.redis)

            # Broadcast sync completion
            await broadcast_to_workspace(
                "ydoc_synced",
                {
                    "ydoc_key": request.ydoc_key,
                    "operations_count": len(request.operations),
                    "synced_by": current_user.id
                },
                f"workspace:{current_user.id}",
                sio
            )

        return {"success": success, "synced_count": len(request.operations)}
    else:
        # Handle realtime operations
        from app.services.socket_service import handle_ydoc_update

        # Combine operations into update data
        from app.services.crdt_service import get_ydoc
        ydoc = await get_ydoc(request.ydoc_key, db)
        if not ydoc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yjs document not found"
            )

        # Apply operations (in real app, would use ypy library)
        # For now, we'll simulate applying to state
        update_data = {"operations": request.operations}

        # Handle through socket service
        success = await handle_ydoc_update(
            request.ydoc_key,
            b"dummy_yjs_state",  # In real app, would be binary Yjs state
            current_user.id,
            current_user.id,  # Using user ID as workspace ID for simplicity
            db,
            sio
        )

        return {"success": success}


@router.get("/presence/{workspace_id}")
async def get_workspace_presence_endpoint(
    workspace_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get all online users and their presence in a workspace.
    """
    online_users = await get_workspace_users(workspace_id, sio_manager.redis)
    cursor_positions = await get_user_cursor_positions(workspace_id, sio_manager.redis)

    return {
        "workspace_id": workspace_id,
        "online_count": len(online_users),
        "online_users": online_users,
        "cursor_positions": cursor_positions,
        "timestamp": "datetime.utcnow().isoformat()"
    }


@router.post("/presence")
async def update_presence_endpoint(
    request: PresenceUpdateRequest,
    current_user = Depends(get_current_user)
):
    """
    Update user's presence status in a workspace.
    """
    await update_user_presence(
        current_user.id,
        request.workspace_id,
        request.status,
        sio_manager.redis
    )

    # Broadcast presence update to other members
    await broadcast_presence_update(request.workspace_id, sio)

    return {"message": "Presence updated"}


@router.post("/typing")
async def update_typing_endpoint(
    request: TypingIndicatorRequest,
    current_user = Depends(get_current_user)
):
    """
    Update typing indicator for a user in a workspace.
    """
    await broadcast_typing_indicator(
        current_user.id,
        current_user.name,
        request.workspace_id,
        request.is_typing,
        sio
    )

    return {"message": "Typing indicator updated"}


@router.post("/cursor")
async def update_cursor_endpoint(
    request: CursorPositionRequest,
    current_user = Depends(get_current_user)
):
    """
    Update user's cursor position for collaborative editing.
    """
    await update_user_cursor_position(
        current_user.id,
        request.workspace_id,
        request.position,
        sio_manager.redis
    )

    # Broadcast cursor position to other users in workspace
    await broadcast_to_workspace(
        "cursor_update",
        {
            "user_id": current_user.id,
            "position": request.position,
            "workspace_id": request.workspace_id
        },
        f"workspace:{request.workspace_id}",
        sio,
        skip_sid=current_user.id
    )

    return {"message": "Cursor position updated"}


@router.post("/offline/queue")
async def queue_offline_operations_endpoint(
    ydoc_key: str,
    operations: List[dict],
    current_user = Depends(get_current_user)
):
    """
    Queue CRDT operations for offline editing.
    Operations will be synced when user reconnects.
    """
    from app.services.offline_service import queue_offline_operations

    key = await queue_offline_operations(
        current_user.id,
        ydoc_key,
        operations,
        sio_manager.redis
    )

    return {"queued": True, "operation_count": len(operations), "key": key}


@router.get("/offline/queued")
async def get_queued_operations_endpoint(
    ydoc_key: str,
    current_user = Depends(get_current_user)
):
    """
    Get all queued CRDT operations for a Yjs document.
    """
    operations = await get_queued_operations(current_user.id, ydoc_key, sio_manager.redis)

    return {
        "ydoc_key": ydoc_key,
        "queued_operations": operations,
        "count": len(operations)
    }


@router.post("/offline/sync")
async def sync_offline_operations_endpoint(
    request: SyncOfflineRequest,
    current_user = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Sync all queued offline operations for a Yjs document.
    """
    # Get all operations
    all_ops = await get_all_user_offline_ops(current_user.id, sio_manager.redis)
    ops = all_ops.get(request.ydoc_key, [])

    if not ops:
        return {"synced": False, "message": "No operations to sync"}

    # Apply operations
    success = await apply_crdt_operations(
        request.ydoc_key,
        ops,
        db
    )

    if success:
        # Clear queued operations
        await clear_queued_operations(current_user.id, request.ydoc_key, sio_manager.redis)

        # Broadcast sync completion
        await broadcast_to_workspace(
            "offline_synced",
            {
                "ydoc_key": request.ydoc_key,
                "synced_count": len(ops),
                "synced_by": current_user.id
            },
            f"workspace:{current_user.id}",
            sio
        )

    return {"synced": success, "operation_count": len(ops)}
