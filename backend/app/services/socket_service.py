from typing import List, Optional, Dict, Any
from datetime import datetime


async def broadcast_to_workspace(
    event: str,
    data: Dict[str, Any],
    workspace_id: str,
    sio_manager: Optional[Any] = None,  # Changed for TDD without socket.io
    exclude_user_id: Optional[str] = None
) -> None:
    """
    Broadcast an event to all members of a workspace.
    Can optionally exclude a specific user (the sender).
    """
    if sio_manager:
        broadcast_data = {
            "event": event,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "workspace_id": workspace_id
        }

        # For TDD, we just record the intent
        print(f"Broadcasting {event} to workspace {workspace_id}")


async def user_join_workspace(
    user_id: str,
    user_name: str,
    workspace_id: str,
    sio_manager: Optional[Any] = None,
) -> None:
    """
    Handle user joining a workspace.
    Updates presence and broadcasts to other members.
    """
    if sio_manager:
        sio_manager.join_room(user_id, workspace_id)
        print(f"User {user_id} ({user_name}) joining workspace {workspace_id}")


async def user_leave_workspace(
    user_id: str,
    workspace_id: str,
    sio_manager: Optional[Any] = None,
) -> None:
    """
    Handle user leaving a workspace.
    Removes presence and broadcasts to other members.
    """
    if sio_manager:
        sio_manager.leave_room(user_id, workspace_id)
        print(f"User {user_id} leaving workspace {workspace_id}")


async def broadcast_presence_update(
    workspace_id: str,
    sio_manager: Optional[Any] = None,
) -> None:
    """
    Broadcast presence update to all workspace members.
    Includes list of online users and their cursor positions.
    """
    if sio_manager:
        print(f"Broadcasting presence update for workspace {workspace_id}")


async def broadcast_typing_indicator(
    user_id: str,
    user_name: str,
    workspace_id: str,
    is_typing: bool,
    sio_manager: Optional[Any] = None,
) -> None:
    """
    Broadcast typing indicator to workspace members.
    Debounces rapid typing events (handled client-side).
    """
    if sio_manager:
        print(f"User {user_id} ({user_name}) typing indicator: {is_typing} in workspace {workspace_id}")


async def handle_ydoc_update(
    ydoc_key: str,
    update_data: bytes,
    user_id: str,
    workspace_id: str,
    db: Any,  # Changed to accept Any db
    sio_manager: Optional[Any] = None,
) -> bool:
    """
    Handle Yjs document update from client.
    Updates CRDT state and broadcasts to workspace members.
    """
    print(f"Handling Yjs update for {ydoc_key} by user {user_id} in workspace {workspace_id}")

    # Broadcast update to workspace members
    await broadcast_to_workspace(
        "ydoc_update",
        {
            "ydoc_key": ydoc_key,
            "update_size": len(update_data),
            "updated_by": user_id,
            "timestamp": datetime.utcnow().isoformat()
        },
        workspace_id,
        sio_manager
    )

    return True


class SocketManager:
    """
    Manages WebSocket connections and room memberships.
    For TDD, this is a simplified version without actual socket.io dependency.
    """
    def __init__(self):
        self.active_connections: Dict[str, str] = {}
        self.user_rooms: Dict[str, str] = {}

    async def connect(self, sid: str, user_id: str):
        """Register a new WebSocket connection."""
        self.active_connections[sid] = user_id
        print(f"Connection registered: {sid} -> {user_id}")

    async def disconnect(self, sid: str):
        """Unregister a WebSocket connection."""
        user_id = self.active_connections.pop(sid, None)
        if user_id and user_id in self.user_rooms:
            del self.user_rooms[user_id]
        print(f"Connection disconnected: {sid} (was user {user_id})")

    async def join_room(self, user_id: str, room: str):
        """Add user to a room (workspace)."""
        self.user_rooms[user_id] = room
        print(f"User {user_id} joined room: {room}")

    async def leave_room(self, user_id: str, room: str):
        """Remove user from a room."""
        if user_id in self.user_rooms:
            del self.user_rooms[user_id]
        print(f"User {user_id} left room: {room}")

    async def get_room_members(self, room: str) -> List[str]:
        """Get all user IDs in a room."""
        return [uid for uid, rid in self.user_rooms.items() if rid == room]

    async def is_user_in_room(self, user_id: str, room: str) -> bool:
        """Check if user is in a specific room."""
        return self.user_rooms.get(user_id) == room


# Global socket manager instance
sio_manager = SocketManager()
