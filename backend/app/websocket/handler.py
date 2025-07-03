"""
WebSocket handler for chat functionality.
"""
import json
from typing import Optional
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.websocket.manager import websocket_manager
from app.core.database import get_db, AsyncSessionLocal
from app.core.security import verify_token
from app.repositories.user_repository import UserRepository
from app.repositories.channel_repository import ChannelRepository, ChannelMemberRepository
from app.repositories.message_repository import MessageRepository
from app.models.user import User


class WebSocketHandler:
    """Handles WebSocket connections and message processing."""
    
    def __init__(self):
        pass
    
    async def handle_connection(self, websocket: WebSocket, token: Optional[str] = None):
        """Handle a new WebSocket connection."""
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No authentication token provided")
            return
        
        try:
            # Verify the token and get user
            user_id_str = verify_token(token)
            if not user_id_str:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
                return
            user_id = UUID(user_id_str)
            
            # Get database session
            db = AsyncSessionLocal()
            try:
                user_repo = UserRepository(db)
                user = await user_repo.get(user_id)
                
                if not user or not user.is_active():
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid user")
                    return
                
                # Accept the connection
                await websocket_manager.connect(websocket, user_id)
                
                try:
                    while True:
                        # Wait for messages from the client
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        await self.handle_message(websocket, user_id, message, db)
                        
                except WebSocketDisconnect:
                    print(f"WebSocket disconnected for user {user_id}")
                except Exception as e:
                    print(f"Error in WebSocket connection: {e}")
                finally:
                    websocket_manager.disconnect(websocket)
            finally:
                await db.close()
                    
        except Exception as e:
            print(f"WebSocket authentication failed: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
    
    async def handle_message(self, websocket: WebSocket, user_id: UUID, message: dict, db: AsyncSession):
        """Handle incoming messages from WebSocket clients."""
        message_type = message.get("type")
        data = message.get("data", {})
        
        try:
            if message_type == "join_channel":
                await self.handle_join_channel(user_id, data, db)
            elif message_type == "leave_channel":
                await self.handle_leave_channel(user_id, data, db)
            elif message_type == "send_message":
                await self.handle_send_message(user_id, data, db)
            elif message_type == "typing":
                await self.handle_typing(user_id, data)
            elif message_type == "update_presence":
                await self.handle_update_presence(user_id, data)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}")
                
        except Exception as e:
            print(f"Error handling WebSocket message: {e}")
            await self.send_error(websocket, f"Error processing message: {str(e)}")
    
    async def handle_join_channel(self, user_id: UUID, data: dict, db: AsyncSession):
        """Handle channel join request."""
        channel_id = UUID(data.get("channel_id"))
        
        # TODO: Verify user has access to the channel
        channel_member_repo = ChannelMemberRepository(db)
        # member = await channel_member_repo.get_channel_member(user_id, channel_id)
        
        # if not member:
        #     print(f"User {user_id} attempted to join channel {channel_id} without permission")
        #     return
        
        # For public channels, allow all authenticated users for now
        print(f"User {user_id} joining channel {channel_id}")
        
        # Subscribe to channel
        await websocket_manager.subscribe_to_channel(user_id, channel_id)
        
        # Notify others that user joined
        await websocket_manager.broadcast_to_channel(channel_id, {
            "type": "user_joined",
            "data": {
                "user_id": str(user_id),
                "channel_id": str(channel_id)
            }
        })
    
    async def handle_leave_channel(self, user_id: UUID, data: dict, db: AsyncSession):
        """Handle channel leave request."""
        channel_id = UUID(data.get("channel_id"))
        
        # Unsubscribe from channel
        await websocket_manager.unsubscribe_from_channel(user_id, channel_id)
        
        # Notify others that user left
        await websocket_manager.broadcast_to_channel(channel_id, {
            "type": "user_left",
            "data": {
                "user_id": str(user_id),
                "channel_id": str(channel_id)
            }
        })
    
    async def handle_send_message(self, user_id: UUID, data: dict, db: AsyncSession):
        """Handle message send request."""
        channel_id = UUID(data.get("channel_id"))
        content = data.get("content")
        reply_to = data.get("reply_to")
        
        # TODO: Verify user has access to the channel
        channel_member_repo = ChannelMemberRepository(db)
        # member = await channel_member_repo.get_channel_member(user_id, channel_id)
        
        # if not member:
        #     print(f"User {user_id} attempted to send message to channel {channel_id} without permission")
        #     return
        
        # For public channels, allow all authenticated users for now
        print(f"User {user_id} sending message to channel {channel_id}")
        
        # Create message in database
        message_repo = MessageRepository(db)
        message = await message_repo.create({
            "channel_id": channel_id,
            "user_id": user_id,
            "content": content,
            "reply_to": UUID(reply_to) if reply_to else None,
            "message_type": "text"
        })
        
        # Get user info for the message
        user_repo = UserRepository(db)
        user = await user_repo.get(user_id)
        
        # Broadcast message to channel subscribers
        await websocket_manager.broadcast_to_channel(channel_id, {
            "type": "new_message",
            "data": {
                "id": str(message.id),
                "channel_id": str(channel_id),
                "user_id": str(user_id),
                "username": user.username,
                "display_name": user.display_name,
                "content": content,
                "reply_to": reply_to,
                "created_at": message.created_at.isoformat(),
                "message_type": "text"
            }
        })
    
    async def handle_typing(self, user_id: UUID, data: dict):
        """Handle typing indicator."""
        channel_id = UUID(data.get("channel_id"))
        is_typing = data.get("is_typing", False)
        
        # Broadcast typing status to channel subscribers
        await websocket_manager.broadcast_to_channel(channel_id, {
            "type": "typing",
            "data": {
                "user_id": str(user_id),
                "channel_id": str(channel_id),
                "is_typing": is_typing
            }
        })
    
    async def handle_update_presence(self, user_id: UUID, data: dict):
        """Handle presence update."""
        status = data.get("status", "online")
        
        # Update user presence in database would go here
        # For now, just broadcast to all user's channels
        print(f"User {user_id} updated presence to {status}")
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """Send an error message to the client."""
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": error_message}
            }))
        except Exception:
            pass  # Connection might be closed


# Global handler instance
websocket_handler = WebSocketHandler()
