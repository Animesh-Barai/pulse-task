from typing import Dict, Any


class SimpleSocketManager:
    """Mock socket manager for testing purposes."""
    
    def __init__(self):
        self.rooms: Dict[str, set] = {}
    
    def join_room(self, sid: str, room: str):
        """Add socket ID to room."""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(sid)
    
    def leave_room(self, sid: str, room: str):
        """Remove socket ID from room."""
        if room in self.rooms:
            self.rooms[room].discard(sid)
    
    def broadcast(self, event: str, room: str, data: Any = None):
        """Broadcast event to all sockets in room."""
        pass


# Global socket manager instance
simple_socket_manager = SimpleSocketManager()


def user_join_workspace(user_id: str, username: str, workspace_id: str):
    """Handle user joining workspace room."""
    simple_socket_manager.join_room(user_id, workspace_id)


def user_leave_workspace(user_id: str, workspace_id: str):
    """Handle user leaving workspace room."""
    simple_socket_manager.leave_room(user_id, workspace_id)


def broadcast_to_workspace(event: str, data: Any, workspace_id: str):
    """Broadcast event to workspace members."""
    simple_socket_manager.broadcast(event, workspace_id, data)


def handle_ydoc_update(ydoc_key: str, update_data: dict):
    """Handle Yjs document update event."""
    pass
