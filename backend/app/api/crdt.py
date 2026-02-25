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
from app.db.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/api/v1/ydocs", tags=["CRDT"])


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
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Create a new Yjs document (list).

    Validates task data, generates unique y_doc_key for CRDT synchronization,
    creates document in database,
    and returns created document with 201 status.
    """
    result = await create_ydoc(ydoc, db)

    # Broadcast Ydoc creation via Socket.IO to workspace
    try:
        task_data = {
            "task_id": result.id,
            "title": result.title,
            "list_id": result.list_id,
            "user_id": current_user["id"],
            "workspace_id": result.list_id,
            "created_at": result.created_at.isoformat()
        }
        emit_task_created(task_data)
    except Exception as e:
        # Log error but don't fail request
        print(f"Warning: Failed to broadcast Ydoc creation: {e}")

    return result


@router.get("/{ydoc_key}", response_model=YDocResponse)
async def get_ydoc_endpoint(
    ydoc_key: str,
    current_user: dict = Depends(get_current_user),
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
            "user_id": current_user["id"]
        }
        broadcast_crdt_update(ydoc.list_id, crdt_data)
    except Exception as e:
        # Log error but don't fail request
        print(f"Failed to broadcast CRDT access: {e}")

    return YDocResponse(
        id=str(ydoc["id"]),
        list_id=ydoc.list_id,
        title=ydoc.title,
        y_doc_key=ydoc.y_doc_key,
        created_at=ydoc.created_at.isoformat(),
        updated_at=ydoc.updated_at.isoformat() if ydoc.updated_at else None
    )


@router.get("/workspace/{workspace_id}", response_model=List[YDocResponse])
async def list_ydocs_endpoint(
    workspace_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    List all Yjs documents belonging to a workspace.
    """
    ydocs = await list_ydocs_by_workspace(workspace_id, db)
    return [YDocResponse(
        id=str(ydoc["id"]),
        list_id=ydoc.list_id,
        title=ydoc.title,
        y_doc_key=ydoc.y_doc_key,
        created_at=ydoc.created_at.isoformat(),
        updated_at=ydoc.updated_at.isoformat() if ydoc.updated_at else None
    ) for ydoc in ydocs]


@router.put("/{ydoc_key}", response_model=YDocResponse)
async def update_ydoc_endpoint(
    ydoc_key: str,
    ydoc_update: dict,
    current_user: dict = Depends(get_current_user),
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

    # Update the document
    result = await update_ydoc_snapshot(ydoc_key, ydoc_update.get("content", ""), db)

    # Broadcast update via Socket.IO
    try:
        crdt_data = {
            "doc_key": ydoc_key,
            "list_id": ydoc.list_id,
            "operation": "update",
            "user_id": current_user["id"],
            "content": ydoc_update.get("content", "")
        }
        broadcast_crdt_update(ydoc.list_id, crdt_data)
    except Exception as e:
        print(f"Failed to broadcast CRDT update: {e}")

    return YDocResponse(
        id=str(result["id"]),
        list_id=result.list_id,
        title=result.title,
        y_doc_key=result.y_doc_key,
        created_at=result.created_at.isoformat(),
        updated_at=result.updated_at.isoformat() if result.updated_at else None
    )


@router.delete("/{ydoc_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ydoc_endpoint(
    ydoc_key: str,
    current_user: dict = Depends(get_current_user),
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
            "user_id": current_user["id"]
        }
        broadcast_crdt_update(ydoc.list_id, crdt_data)
    except Exception as e:
        print(f"Failed to broadcast CRDT deletion: {e}")

    return None
