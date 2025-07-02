"""
User-related schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import BaseSchema, TimestampMixin


class UserBase(BaseSchema):
    """Base user schema with common fields."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    display_name: str = Field(..., min_length=1, max_length=100, description="Display name")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")
    timezone: str = Field(default="UTC", description="User's timezone")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()


class UserCreate(UserBase):
    """Schema for user creation."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (minimum 8 characters)"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        
        if not (has_letter and has_number):
            raise ValueError("Password must contain at least one letter and one number")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "display_name": "John Doe",
                "password": "securePassword123",
                "timezone": "America/New_York"
            }
        }


class UserUpdate(BaseSchema):
    """Schema for user updates."""
    
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "display_name": "John Smith",
                "avatar_url": "https://example.com/avatar.jpg",
                "timezone": "Europe/London"
            }
        }


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response."""
    
    id: UUID
    status: str
    email_verified: bool
    last_seen_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "email": "john@example.com",
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "status": "active",
                "timezone": "America/New_York",
                "email_verified": True,
                "last_seen_at": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }


class UserProfile(BaseSchema):
    """Schema for user profile (public information)."""
    
    id: UUID
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    status: str
    last_seen_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "status": "active",
                "last_seen_at": "2024-01-01T12:00:00Z"
            }
        }