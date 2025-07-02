"""
Authentication service for user authentication and authorization.
"""
from datetime import timedelta
from typing import Optional
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse, TokenResponse
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user data
            
        Raises:
            ConflictError: If email or username already exists
        """
        # Check if email already exists
        if await self.user_repository.email_exists(user_data.email):
            raise ConflictError(
                message="Email address is already registered",
                details={"field": "email", "value": user_data.email}
            )
        
        # Check if username already exists
        if await self.user_repository.username_exists(user_data.username):
            raise ConflictError(
                message="Username is already taken",
                details={"field": "username", "value": user_data.username}
            )
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        user = User(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            password_hash=password_hash,
            display_name=user_data.display_name,
            avatar_url=user_data.avatar_url,
            timezone=user_data.timezone,
        )
        
        created_user = await self.user_repository.create(user)
        return UserResponse.model_validate(created_user)
    
    async def authenticate_user(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Login response with user data and tokens
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active():
            raise AuthenticationError("Account is not active")
        
        # Update last seen
        await self.user_repository.update_last_seen(user.id)
        
        # Generate tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        return LoginResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            New token response
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # Verify refresh token
        user_id_str = verify_token(refresh_token)
        if not user_id_str:
            raise AuthenticationError("Invalid refresh token")
        
        # Get user
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid refresh token")
        
        user = await self.user_repository.get_active_user(user_id)
        if not user:
            raise AuthenticationError("User not found or inactive")
        
        # Generate new tokens
        access_token = create_access_token(subject=str(user.id))
        new_refresh_token = create_refresh_token(subject=str(user.id))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def get_current_user(self, token: str) -> UserResponse:
        """
        Get current user from access token.
        
        Args:
            token: JWT access token
            
        Returns:
            Current user data
            
        Raises:
            AuthenticationError: If token is invalid or user not found
        """
        # Verify token
        user_id_str = verify_token(token)
        if not user_id_str:
            raise AuthenticationError("Invalid access token")
        
        # Get user
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid access token")
        
        user = await self.user_repository.get_active_user(user_id)
        if not user:
            raise AuthenticationError("User not found or inactive")
        
        return UserResponse.model_validate(user)
    
    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user's password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            AuthenticationError: If current password is incorrect
            NotFoundError: If user not found
        """
        # Get user
        user = await self.user_repository.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = get_password_hash(new_password)
        
        # Update password
        await self.user_repository.update(user_id, {"password_hash": new_password_hash})
        
        return True
    
    async def verify_email(self, user_id: UUID) -> bool:
        """
        Mark user's email as verified.
        
        Args:
            user_id: User ID
            
        Returns:
            True if email verified successfully
            
        Raises:
            NotFoundError: If user not found
        """
        success = await self.user_repository.verify_email(user_id)
        if not success:
            raise NotFoundError("User not found")
        
        return True