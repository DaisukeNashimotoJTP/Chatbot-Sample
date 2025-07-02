"""
User repository for database operations.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User instance or None
        """
        query = select(User).where(
            User.email == email.lower(),
            User.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        query = select(User).where(
            User.username == username.lower(),
            User.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_user(self, user_id: UUID) -> Optional[User]:
        """
        Get active user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance if active, None otherwise
        """
        user = await self.get(user_id)
        if user and user.is_active():
            return user
        return None
    
    async def email_exists(self, email: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email to check
            exclude_user_id: User ID to exclude from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        query = select(User).where(
            User.email == email.lower(),
            User.deleted_at.is_(None)
        )
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def username_exists(self, username: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """
        Check if username already exists.
        
        Args:
            username: Username to check
            exclude_user_id: User ID to exclude from check (for updates)
            
        Returns:
            True if username exists, False otherwise
        """
        query = select(User).where(
            User.username == username.lower(),
            User.deleted_at.is_(None)
        )
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def update_last_seen(self, user_id: UUID) -> bool:
        """
        Update user's last seen timestamp.
        
        Args:
            user_id: User ID
            
        Returns:
            True if updated, False if user not found
        """
        user = await self.get(user_id)
        if not user:
            return False
        
        user.last_seen_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def verify_email(self, user_id: UUID) -> bool:
        """
        Mark user's email as verified.
        
        Args:
            user_id: User ID
            
        Returns:
            True if updated, False if user not found
        """
        user = await self.get(user_id)
        if not user:
            return False
        
        user.email_verified = True
        await self.db.commit()
        return True
    
    async def change_user_status(self, user_id: UUID, status: str) -> bool:
        """
        Change user status.
        
        Args:
            user_id: User ID
            status: New status (active, inactive, suspended)
            
        Returns:
            True if updated, False if user not found
        """
        if status not in ["active", "inactive", "suspended"]:
            raise ValueError("Invalid status. Must be one of: active, inactive, suspended")
        
        user = await self.get(user_id)
        if not user:
            return False
        
        user.status = status
        await self.db.commit()
        return True