"""
Message-related schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseSchema, TimestampMixin


class MessageBase(BaseSchema):
    """Base message schema."""
    
    content: Optional[str] = Field(None, description="Message content")
    message_type: str = Field(default="text", description="Message type: text, file, system")
    
    @field_validator("message_type")
    @classmethod
    def validate_message_type(cls, v: str) -> str:
        """Validate message type."""
        if v not in ["text", "file", "system"]:
            raise ValueError("Message type must be 'text', 'file', or 'system'")
        return v


class MessageCreate(MessageBase):
    """Schema for message creation."""
    
    content: str = Field(..., min_length=1, max_length=4000, description="Message content")
    reply_to: Optional[UUID] = Field(None, description="Message ID this is a reply to")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="File attachments")
    mentions: Optional[List[UUID]] = Field(None, description="List of mentioned user IDs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello, world!",
                "message_type": "text",
                "reply_to": None,
                "mentions": ["550e8400-e29b-41d4-a716-446655440000"]
            }
        }


class MessageUpdate(BaseSchema):
    """Schema for message updates."""
    
    content: str = Field(..., min_length=1, max_length=4000, description="Updated message content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Updated message content"
            }
        }


class MessageResponse(MessageBase, TimestampMixin):
    """Schema for message response."""
    
    id: UUID
    channel_id: UUID
    user_id: UUID
    reply_to: Optional[UUID] = None
    thread_ts: Optional[datetime] = None
    reply_count: int = 0
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    mentions: Optional[List[UUID]] = None
    
    # User information (populated from join)
    user_username: Optional[str] = None
    user_display_name: Optional[str] = None
    user_avatar_url: Optional[str] = None
    
    # Reaction summary
    reaction_counts: Optional[Dict[str, int]] = None
    user_reactions: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "channel_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440002",
                "content": "Hello, world!",
                "message_type": "text",
                "reply_to": None,
                "reply_count": 0,
                "is_edited": False,
                "user_username": "johndoe",
                "user_display_name": "John Doe",
                "user_avatar_url": "https://example.com/avatar.jpg",
                "reaction_counts": {"👍": 2, "❤️": 1},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class MessageList(BaseSchema):
    """Schema for message list with pagination."""
    
    messages: List[MessageResponse]
    total: int
    has_more: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "content": "Hello, world!",
                        "user_username": "johndoe",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 100,
                "has_more": True
            }
        }


class MessageReactionCreate(BaseSchema):
    """Schema for adding message reaction."""
    
    emoji: str = Field(..., min_length=1, max_length=10, description="Reaction emoji")
    
    @field_validator("emoji")
    @classmethod
    def validate_emoji(cls, v: str) -> str:
        """Validate emoji format."""
        # Simple validation - in production, you might want more sophisticated emoji validation
        if len(v.strip()) == 0:
            raise ValueError("Emoji cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "emoji": "👍"
            }
        }


class MessageReactionResponse(BaseSchema):
    """Schema for message reaction response."""
    
    id: UUID
    message_id: UUID
    user_id: UUID
    emoji: str
    created_at: datetime
    
    # User information
    user_username: str
    user_display_name: str
    user_avatar_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "message_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440002",
                "emoji": "👍",
                "user_username": "johndoe",
                "user_display_name": "John Doe",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class ThreadResponse(BaseSchema):
    """Schema for thread response."""
    
    parent_message: MessageResponse
    replies: List[MessageResponse]
    total_replies: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "parent_message": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "content": "Parent message",
                    "user_username": "johndoe"
                },
                "replies": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "content": "Reply message",
                        "user_username": "janedoe"
                    }
                ],
                "total_replies": 1
            }
        }