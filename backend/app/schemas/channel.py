"""
Channel-related schemas.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseSchema, TimestampMixin


class ChannelBase(BaseSchema):
    """Base channel schema."""
    
    name: str = Field(..., min_length=1, max_length=80, description="Channel name")
    description: Optional[str] = Field(None, description="Channel description")
    type: str = Field(default="public", description="Channel type: public, private")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate channel name format."""
        # Remove # prefix if present
        if v.startswith("#"):
            v = v[1:]
        
        # Channel names should be lowercase and contain only letters, numbers, hyphens, underscores
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Channel name can only contain letters, numbers, hyphens, and underscores")
        
        return v.lower()
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate channel type."""
        if v not in ["public", "private"]:
            raise ValueError("Channel type must be 'public' or 'private'")
        return v


class ChannelCreate(ChannelBase):
    """Schema for channel creation."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "general",
                "description": "General discussion channel",
                "type": "public"
            }
        }


class ChannelUpdate(BaseSchema):
    """Schema for channel updates."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=80)
    description: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate channel name format."""
        if v is None:
            return v
        
        # Remove # prefix if present
        if v.startswith("#"):
            v = v[1:]
        
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Channel name can only contain letters, numbers, hyphens, and underscores")
        
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "updated-channel-name",
                "description": "Updated channel description"
            }
        }


class ChannelResponse(ChannelBase, TimestampMixin):
    """Schema for channel response."""
    
    id: UUID
    workspace_id: UUID
    created_by: UUID
    is_archived: bool
    member_count: Optional[int] = None
    unread_count: Optional[int] = None
    user_role: Optional[str] = None
    last_message: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "workspace_id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "general",
                "description": "General discussion",
                "type": "public",
                "created_by": "550e8400-e29b-41d4-a716-446655440002",
                "is_archived": False,
                "member_count": 15,
                "unread_count": 3,
                "user_role": "member",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class ChannelMemberResponse(BaseSchema):
    """Schema for channel member information."""
    
    user_id: UUID
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    role: str
    joined_at: datetime
    last_read_at: Optional[datetime] = None
    notification_level: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "role": "member",
                "joined_at": "2024-01-01T00:00:00Z",
                "last_read_at": "2024-01-01T12:00:00Z",
                "notification_level": "all"
            }
        }


class ChannelMembersList(BaseSchema):
    """Schema for channel members list."""
    
    members: List[ChannelMemberResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "members": [
                    {
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "johndoe",
                        "display_name": "John Doe",
                        "role": "member",
                        "joined_at": "2024-01-01T00:00:00Z",
                        "notification_level": "all"
                    }
                ],
                "total": 10
            }
        }


class ChannelInvite(BaseSchema):
    """Schema for channel invitation."""
    
    user_ids: List[UUID] = Field(..., description="List of user IDs to invite to channel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "550e8400-e29b-41d4-a716-446655440001"
                ]
            }
        }