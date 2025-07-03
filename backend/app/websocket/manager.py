"""
WebSocket connection manager.
"""
import json
import asyncio
from typing import Dict, List, Set, Optional
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        # user_id -> List[WebSocket]
        self.user_connections: Dict[UUID, List[WebSocket]] = {}
        # channel_id -> Set[user_id]
        self.channel_subscriptions: Dict[UUID, Set[UUID]] = {}
        # websocket -> user_id
        self.connection_users: Dict[WebSocket, UUID] = {}
    
    async def connect(self, websocket: WebSocket, user_id: UUID):
        """Accept a WebSocket connection and associate it with a user."""
        await websocket.accept()
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        self.user_connections[user_id].append(websocket)
        self.connection_users[websocket] = user_id
        
        print(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket and clean up associations."""
        user_id = self.connection_users.get(websocket)
        if user_id:
            if user_id in self.user_connections:
                self.user_connections[user_id].remove(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from all channel subscriptions
            for channel_id, users in self.channel_subscriptions.items():
                users.discard(user_id)
            
            del self.connection_users[websocket]
            print(f"User {user_id} disconnected from WebSocket")
    
    async def subscribe_to_channel(self, user_id: UUID, channel_id: UUID):
        """Subscribe a user to a channel for message broadcasting."""
        if channel_id not in self.channel_subscriptions:
            self.channel_subscriptions[channel_id] = set()
        
        self.channel_subscriptions[channel_id].add(user_id)
        print(f"User {user_id} subscribed to channel {channel_id}")
    
    async def unsubscribe_from_channel(self, user_id: UUID, channel_id: UUID):
        """Unsubscribe a user from a channel."""
        if channel_id in self.channel_subscriptions:
            self.channel_subscriptions[channel_id].discard(user_id)
            print(f"User {user_id} unsubscribed from channel {channel_id}")
    
    async def send_personal_message(self, message: dict, user_id: UUID):
        """Send a message to a specific user across all their connections."""
        if user_id in self.user_connections:
            connections = self.user_connections[user_id]
            await asyncio.gather(
                *[self._send_safe(conn, message) for conn in connections],
                return_exceptions=True
            )
    
    async def broadcast_to_channel(self, channel_id: UUID, message: dict):
        """Broadcast a message to all users subscribed to a channel."""
        print(f"Broadcasting message to channel {channel_id}: {message}")
        if channel_id in self.channel_subscriptions:
            users = self.channel_subscriptions[channel_id]
            print(f"Channel {channel_id} has {len(users)} subscribed users: {users}")
            tasks = []
            
            for user_id in users:
                if user_id in self.user_connections:
                    connections = self.user_connections[user_id]
                    print(f"User {user_id} has {len(connections)} active connections")
                    tasks.extend([
                        self._send_safe(conn, message) for conn in connections
                    ])
            
            if tasks:
                print(f"Sending message to {len(tasks)} connections")
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                print("No tasks to send message to")
        else:
            print(f"Channel {channel_id} has no subscriptions")
    
    async def _send_safe(self, websocket: WebSocket, message: dict):
        """Safely send a message to a WebSocket connection."""
        try:
            message_str = json.dumps(message)
            print(f"Sending WebSocket message: {message_str}")
            await websocket.send_text(message_str)
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")
            # Connection might be closed, ignore
            pass
    
    def get_channel_user_count(self, channel_id: UUID) -> int:
        """Get the number of users currently subscribed to a channel."""
        return len(self.channel_subscriptions.get(channel_id, set()))
    
    def get_user_connection_count(self, user_id: UUID) -> int:
        """Get the number of active connections for a user."""
        return len(self.user_connections.get(user_id, []))


# Singleton instance
websocket_manager = ConnectionManager()
