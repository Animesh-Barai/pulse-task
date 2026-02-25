"""
Socket.IO Event Handlers

Real-time event handlers for PulseTasks collaboration features.
"""
from typing import Dict, Any
from socketio import AsyncServer
from datetime import datetime
from app.db.database import get_redis
from app.services.presence_service import (
    update_user_presence,
    set_user_typing,
    update_cursor_position,
    remove_user_presence
)
import logging

logger = logging.getLogger(__name__)

# Global reference to socketio server (will be set from main.py)
sio_server: AsyncServer = None


def register_socket_events(sio: AsyncServer) -> None:
    """
    Register all Socket.IO event handlers.

    Args:
        sio: Socket.IO AsyncServer instance
    """
    global sio_server
    sio_server = sio

    @sio.event
    async def connect(sid: str, environ: Dict[str, Any]):
        """Handle client connection."""
        logger.info(f"Client connected: {sid}")

        # Store connection info in session
        await sio.save_session(sid, {
            "connected_at": datetime.utcnow().isoformat(),
            "user_id": environ.get("user_id"),
            "user_name": environ.get("user_name"),
            "workspace_id": environ.get("workspace_id")
        })

        # Update presence to online in Redis
        user_id = environ.get("user_id")
        workspace_id = environ.get("workspace_id")
        user_name = environ.get("user_name")

        if user_id and workspace_id:
            redis = get_redis()
            await update_user_presence(
                user_id=user_id,
                workspace_id=workspace_id,
                presence="online",
                user_name=user_name,
                redis_client=redis
            )

        logger.info(f"Session saved and presence updated for sid: {sid}")

    @sio.event
    async def disconnect(sid: str):
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {sid}")

        # Get session data
        session = await sio.get_session(sid)
        if session:
            user_id = session.get("user_id")
            workspace_id = session.get("workspace_id")

            # Remove presence from Redis
            if user_id and workspace_id:
                redis = get_redis()
                await remove_user_presence(
                    user_id=user_id,
                    workspace_id=workspace_id,
                    redis_client=redis
                )

        logger.info(f"Session and presence cleaned up for sid: {sid}")

    @sio.event
    async def join_workspace(sid: str, data: Dict[str, Any]):
        """User joins a workspace."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")
        user_name = data.get("user_name")

        if not workspace_id or not user_id:
            logger.warning(f"Invalid join_workspace data: {data}")
            return

        logger.info(f"User {user_id} joining workspace {workspace_id}")

        # Join socket room
        await sio.enter_room(sid, workspace_id)

        # Update presence to online in Redis
        redis = get_redis()
        await update_user_presence(
            user_id=user_id,
            workspace_id=workspace_id,
            presence="online",
            user_name=user_name,
            redis_client=redis
        )

        # Broadcast join to other users
        await sio.emit(
            "user_joined",
            {
                "user_id": user_id,
                "user_name": user_name,
                "workspace_id": workspace_id,
                "joined_at": datetime.utcnow().isoformat()
            },
            room=workspace_id,
            skip_sid=sid
        )

        logger.info(f"User {user_id} joined room {workspace_id}")

    @sio.event
    async def leave_workspace(sid: str, data: Dict[str, Any]):
        """User leaves a workspace."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")
        user_name = data.get("user_name")

        if not workspace_id or not user_id:
            logger.warning(f"Invalid leave_workspace data: {data}")
            return

        logger.info(f"User {user_id} leaving workspace {workspace_id}")

        # Leave socket room
        await sio.leave_room(sid, workspace_id)

        # Remove presence from Redis
        redis = get_redis()
        await remove_user_presence(
            user_id=user_id,
            workspace_id=workspace_id,
            redis_client=redis
        )

        # Broadcast leave to workspace
        await sio.emit(
            "user_left",
            {
                "user_id": user_id,
                "user_name": user_name,
                "workspace_id": workspace_id,
                "left_at": datetime.utcnow().isoformat()
            },
            room=workspace_id
        )

        logger.info(f"User {user_id} left room {workspace_id}")

    @sio.event
    async def cursor_position(sid: str, data: Dict[str, Any]):
        """Broadcast user's cursor position (collaboration)."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")
        list_id = data.get("list_id")
        task_id = data.get("task_id")
        position = data.get("position")

        if not workspace_id or not user_id:
            logger.warning(f"Invalid cursor_position data: {data}")
            return

        logger.info(f"Cursor position update for user {user_id} in workspace {workspace_id}")

        # Update cursor in Redis
        redis = get_redis()
        await update_cursor_position(
            user_id=user_id,
            workspace_id=workspace_id,
            list_id=list_id,
            task_id=task_id,
            position=position,
            redis_client=redis
        )

        # Broadcast cursor position to workspace
        await sio.emit(
            "cursor_moved",
            {
                "user_id": user_id,
                "list_id": list_id,
                "task_id": task_id,
                "position": position,
                "updated_at": datetime.utcnow().isoformat()
            },
            room=workspace_id,
            skip_sid=sid
        )

    @sio.event
    async def start_typing(sid: str, data: Dict[str, Any]):
        """User starts typing."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")

        if not workspace_id or not user_id:
            logger.warning(f"Invalid start_typing data: {data}")
            return

        logger.info(f"User {user_id} started typing in workspace {workspace_id}")

        # Update typing status in Redis
        redis = get_redis()
        await set_user_typing(
            user_id=user_id,
            workspace_id=workspace_id,
            is_typing=True,
            redis_client=redis
        )

        # Broadcast typing indicator
        await sio.emit(
            "user_typing",
            {
                "user_id": user_id,
                "is_typing": True,
                "timestamp": datetime.utcnow().isoformat()
            },
            room=workspace_id
        )

    @sio.event
    async def stop_typing(sid: str, data: Dict[str, Any]):
        """User stops typing."""
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id")

        if not workspace_id or not user_id:
            logger.warning(f"Invalid stop_typing data: {data}")
            return

        logger.info(f"User {user_id} stopped typing in workspace {workspace_id}")

        # Update typing status in Redis
        redis = get_redis()
        await set_user_typing(
            user_id=user_id,
            workspace_id=workspace_id,
            is_typing=False,
            redis_client=redis
        )

        # Broadcast typing indicator
        await sio.emit(
            "user_typing",
            {
                "user_id": user_id,
                "is_typing": False,
                "timestamp": datetime.utcnow().isoformat()
            },
            room=workspace_id
        )

    @sio.event
    async def task_updated(sid: str, data: Dict[str, Any]):
        """Broadcast task update to all users in workspace."""
        workspace_id = data.get("workspace_id")
        task_id = data.get("task_id")

        logger.info(f"Task {task_id} updated in workspace {workspace_id}")

        # Broadcast update
        await sio.emit(
            "task_updated",
            data,
            room=workspace_id
        )

    @sio.event
    async def task_created(sid: str, data: Dict[str, Any]):
        """Broadcast new task creation to all users in workspace."""
        workspace_id = data.get("workspace_id")

        logger.info(f"Task created in workspace {workspace_id}")

        # Broadcast creation
        await sio.emit(
            "task_created",
            data,
            room=workspace_id
        )

    @sio.event
    async def task_deleted(sid: str, data: Dict[str, Any]):
        """Broadcast task deletion to all users in workspace."""
        workspace_id = data.get("workspace_id")
        task_id = data.get("task_id")

        logger.info(f"Task {task_id} deleted in workspace {workspace_id}")

        # Broadcast deletion
        await sio.emit(
            "task_deleted",
            data,
            room=workspace_id
        )

    @sio.event
    async def crdt_update(sid: str, data: Dict[str, Any]):
        """Receive and broadcast CRDT document updates."""
        workspace_id = data.get("workspace_id")
        doc_key = data.get("doc_key")

        logger.info(f"CRDT update for {doc_key} in workspace {workspace_id}")

        # Broadcast CRDT update to all users in workspace
        await sio.emit(
            "crdt_update",
            data,
            room=workspace_id,
            skip_sid=sid
        )


def emit_task_created(task_data: Dict[str, Any]) -> None:
    """
    Helper function to emit task_created event.
    Can be called from REST API endpoints.

    Args:
        task_data: Task data including task_id, workspace_id, etc.
    """
    if sio_server:
        workspace_id = task_data.get("workspace_id")
        sio_server.emit(
            "task_created",
            {
                **task_data,
                "created_at": datetime.utcnow().isoformat()
            },
            room=workspace_id
        )
        logger.info(f"Task created broadcast for workspace {workspace_id}")


def emit_task_updated(task_data: Dict[str, Any]) -> None:
    """
    Helper function to emit task_updated event.
    Can be called from REST API endpoints.

    Args:
        task_data: Task data including task_id, workspace_id, etc.
    """
    if sio_server:
        workspace_id = task_data.get("workspace_id")
        sio_server.emit(
            "task_updated",
            {
                **task_data,
                "updated_at": datetime.utcnow().isoformat()
            },
            room=workspace_id
        )
        logger.info(f"Task updated broadcast for workspace {workspace_id}")


def emit_task_deleted(task_data: Dict[str, Any]) -> None:
    """
    Helper function to emit task_deleted event.
    Can be called from REST API endpoints.

    Args:
        task_data: Task data including task_id, workspace_id, etc.
    """
    if sio_server:
        workspace_id = task_data.get("workspace_id")
        sio_server.emit(
            "task_deleted",
            {
                **task_data,
                "deleted_at": datetime.utcnow().isoformat()
            },
            room=workspace_id
        )
        logger.info(f"Task deleted broadcast for workspace {workspace_id}")


def broadcast_crdt_update(workspace_id: str, crdt_data: Dict[str, Any]) -> None:
    """
    Helper function to broadcast CRDT document update to workspace.
    Can be called from REST API endpoints.

    Args:
        workspace_id: Workspace ID to broadcast to
        crdt_data: CRDT update data including doc_key, operation, etc.
    """
    if sio_server:
        sio_server.emit(
            "crdt_update",
            {
                **crdt_data,
                "updated_at": datetime.utcnow().isoformat()
            },
            room=workspace_id
        )
        logger.info(f"CRDT update broadcast for workspace {workspace_id}")
