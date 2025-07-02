"""
Authentication-related schemas.
"""
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema
from app.schemas.user import UserResponse


class LoginRequest(BaseSchema):
    """Schema for login request."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securePassword123"
            }
        }


class TokenData(BaseSchema):
    """Schema for token data."""
    
    user_id: Optional[UUID] = None


class TokenResponse(BaseSchema):
    """Schema for token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class LoginResponse(BaseSchema):
    """Schema for login response."""
    
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "johndoe",
                    "email": "john@example.com",
                    "display_name": "John Doe",
                    "status": "active",
                    "email_verified": True
                },
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class RefreshTokenRequest(BaseSchema):
    """Schema for refresh token request."""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }


class PasswordChangeRequest(BaseSchema):
    """Schema for password change request."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldPassword123",
                "new_password": "newSecurePassword456"
            }
        }


class PasswordResetRequest(BaseSchema):
    """Schema for password reset request."""
    
    email: EmailStr = Field(..., description="Email address for password reset")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com"
            }
        }


class PasswordResetConfirm(BaseSchema):
    """Schema for password reset confirmation."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "new_password": "newSecurePassword456"
            }
        }