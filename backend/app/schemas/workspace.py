"""
Workspace-related schemas.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseSchema, TimestampMixin


class WorkspaceBase(BaseSchema):
    """Base workspace schema."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    avatar_url: Optional[str] = Field(None, description="Workspace avatar URL")
    is_public: bool = Field(default=False, description="Whether workspace is public")


class WorkspaceCreate(WorkspaceBase):
    """Schema for workspace creation."""
    
    slug: Optional[str] = Field(None, min_length=3, max_length=50, description="URL slug (auto-generated if not provided)")
    
    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Validate slug format."""
        if v is None:
            return v
        
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Slug can only contain letters, numbers, hyphens, and underscores")
        
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Development Team",
                "slug": "dev-team",
                "description": "Workspace for development team collaboration",
                "is_public": False
            }
        }


class WorkspaceUpdate(BaseSchema):
    """Schema for workspace updates."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Team Name",
                "description": "Updated description"
            }
        }


class WorkspaceResponse(WorkspaceBase, TimestampMixin):
    """Schema for workspace response."""
    
    id: UUID
    slug: str
    owner_id: UUID
    invite_code: Optional[str] = None
    max_members: int
    member_count: Optional[int] = None
    user_role: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Development Team",
                "slug": "dev-team",
                "description": "Workspace for development team",
                "owner_id": "550e8400-e29b-41d4-a716-446655440001",
                "is_public": False,
                "invite_code": "abc123def",
                "max_members": 1000,
                "member_count": 15,
                "user_role": "admin",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class WorkspaceInvite(BaseSchema):
    """Schema for workspace invitation."""
    
    invite_code: str = Field(..., description="Workspace invite code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "invite_code": "abc123def"
            }
        }


class UserWorkspaceResponse(BaseSchema):
    """Schema for user-workspace relationship."""
    
    id: UUID
    user_id: UUID
    workspace_id: UUID
    role: str
    joined_at: datetime
    left_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "workspace_id": "550e8400-e29b-41d4-a716-446655440002",
                "role": "member",
                "joined_at": "2024-01-01T00:00:00Z"
            }
        }


class WorkspaceMember(BaseSchema):
    """Schema for workspace member information."""
    
    user_id: UUID
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    role: str
    joined_at: datetime
    last_seen_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "role": "member",
                "joined_at": "2024-01-01T00:00:00Z",
                "last_seen_at": "2024-01-01T12:00:00Z"
            }
        }


class WorkspaceMembersList(BaseSchema):
    """Schema for workspace members list."""
    
    members: List[WorkspaceMember]
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
                        "joined_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 15
            }
        }