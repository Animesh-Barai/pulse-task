"""
Presence API Endpoints

REST API endpoints for real-time presence tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.models.models import User
from app.db.database import get_redis
from app.services.presence_service import (
    get_workspace_users,
    update_user_presence,
    set_user_typing,
    get_user_typing_status,
    get_cursor_positions,
    remove_user_presence
)


router = APIRouter(prefix="/api/v1/presence", tags=["presence"])


# Request/Response Models

class UserPresenceResponse(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    presence: str
    cursor: Optional[Dict[str, Any]] = None
    timestamp: float
    last_seen: str


class WorkspaceUsersResponse(BaseModel):
    workspace_id: str
    users: List[UserPresenceResponse]
    total_count: int


class TypingIndicatorRequest(BaseModel):
    workspace_id: str
    is_typing: bool


class TypingStatusResponse(BaseModel):
    workspace_id: str
    typing_users: List[str]


class CursorPositionRequest(BaseModel):
    workspace_id: str
    list_id: Optional[str] = None
    task_id: Optional[str] = None
    position: Dict[str, Any]


class CursorPositionsResponse(BaseModel):
    workspace_id: str
    cursor_positions: Dict[str, Dict[str, Any]]


# API Endpoints

@router.get("/workspaces/{workspace_id}", response_model=WorkspaceUsersResponse)
async def get_workspace_presence(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all users with presence status in a workspace.

    Returns user presence including cursor positions and typing indicators.
    """
    redis = get_redis()

    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not available"
        )

    try:
        users = await get_workspace_users(workspace_id, redis_client=redis)

        # Convert to response format
        presence_responses = []
        for user_data in users:
            presence_response = UserPresenceResponse(
                user_id=user_data.get("user_id"),
                user_name=user_data.get("user_name"),
                presence=user_data.get("presence", "offline"),
                cursor=user_data.get("cursor"),
                timestamp=user_data.get("timestamp"),
                last_seen=user_data.get("last_seen")
            )
            presence_responses.append(presence_response)

        return WorkspaceUsersResponse(
            workspace_id=workspace_id,
            users=presence_responses,
            total_count=len(presence_responses)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving workspace presence: {str(e)}"
        )


@router.post("/typing", status_code=status.HTTP_200_OK)
async def set_typing_indicator(
    request: TypingIndicatorRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Set or clear user's typing indicator in a workspace.

    Updates Redis and triggers Socket.IO broadcast.
    """
    redis = get_redis()

    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not available"
        )

    try:
        success = await set_user_typing(
            user_id=current_user.id,
            workspace_id=request.workspace_id,
            is_typing=request.is_typing,
            redis_client=redis
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update typing indicator"
            )

        return {"status": "success", "is_typing": request.is_typing}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting typing indicator: {str(e)}"
        )


@router.get("/typing/{workspace_id}", response_model=TypingStatusResponse)
async def get_typing_status(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get typing status for all users in a workspace.

    Returns list of user IDs who are currently typing.
    """
    redis = get_redis()

    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not available"
        )

    try:
        # Get all users in workspace first
        users = await get_workspace_users(workspace_id, redis_client=redis)
        user_ids = [u.get("user_id") for u in users]

        # Get typing status for all users
        typing_status = await get_user_typing_status(
            workspace_id=workspace_id,
            user_ids=user_ids,
            redis_client=redis
        )

        # Filter users who are typing
        typing_users = [uid for uid, is_typing in typing_status.items() if is_typing]

        return TypingStatusResponse(
            workspace_id=workspace_id,
            typing_users=typing_users
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving typing status: {str(e)}"
        )


@router.post("/cursor", status_code=status.HTTP_200_OK)
async def update_cursor_position(
    request: CursorPositionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's cursor position in a workspace.

    Updates Redis and triggers Socket.IO broadcast.
    """
    redis = get_redis()

    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not available"
        )

    try:
        success = await update_cursor_position(
            user_id=current_user.id,
            workspace_id=request.workspace_id,
            list_id=request.list_id,
            task_id=request.task_id,
            position=request.position,
            redis_client=redis
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update cursor position"
            )

        return {
            "status": "success",
            "workspace_id": request.workspace_id,
            "position": request.position
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating cursor position: {str(e)}"
        )


@router.get("/cursors/{workspace_id}", response_model=CursorPositionsResponse)
async def get_all_cursor_positions(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get cursor positions for all users in a workspace.

    Returns mapping of user IDs to their cursor positions.
    """
    redis = get_redis()

    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not available"
        )

    try:
        # Get all users in workspace first
        users = await get_workspace_users(workspace_id, redis_client=redis)
        user_ids = [u.get("user_id") for u in users]

        # Get cursor positions
        cursor_positions = await get_cursor_positions(
            workspace_id=workspace_id,
            user_ids=user_ids,
            redis_client=redis
        )

        return CursorPositionsResponse(
            workspace_id=workspace_id,
            cursor_positions=cursor_positions
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cursor positions: {str(e)}"
        )


@router.delete("/users/{user_id}/workspaces/{workspace_id}", status_code=status.HTTP_200_OK)
async def remove_user_from_workspace(
    user_id: str,
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove user's presence from a workspace.

    Called on disconnect or manual leave.
    """
    redis = get_redis()

    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not available"
        )

    try:
        success = await remove_user_presence(
            user_id=user_id,
            workspace_id=workspace_id,
            redis_client=redis
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove user presence"
            )

        return {
            "status": "success",
            "message": f"User {user_id} removed from workspace {workspace_id}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing user presence: {str(e)}"
        )


@router.post("/cleanup/{workspace_id}", status_code=status.HTTP_200_OK)
async def cleanup_workspace_presence(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Clean up expired presence entries for a workspace.

    Manually trigger cleanup of expired keys.
    Redis handles TTL automatically, but this can be used to force cleanup.
    """
    redis = get_redis()

    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not available"
        )

    try:
        cleaned_count = await cleanup_expired_presence(
            workspace_id=workspace_id,
            redis_client=redis
        )

        return {
            "status": "success",
            "workspace_id": workspace_id,
            "cleaned_count": cleaned_count,
            "message": f"Cleaned up {cleaned_count} expired keys"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up presence: {str(e)}"
        )
