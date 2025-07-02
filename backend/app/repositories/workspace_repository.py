"""
Workspace repository for database operations.
"""
import secrets
import string
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workspace import Workspace, UserWorkspace
from app.models.user import User
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    """Repository for Workspace model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Workspace, db)
    
    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        """
        Get workspace by slug.
        
        Args:
            slug: Workspace slug
            
        Returns:
            Workspace instance or None
        """
        query = select(Workspace).where(
            Workspace.slug == slug,
            Workspace.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_invite_code(self, invite_code: str) -> Optional[Workspace]:
        """
        Get workspace by invite code.
        
        Args:
            invite_code: Workspace invite code
            
        Returns:
            Workspace instance or None
        """
        query = select(Workspace).where(
            Workspace.invite_code == invite_code,
            Workspace.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_workspaces(
        self,
        user_id: UUID,
        include_left: bool = False
    ) -> List[Workspace]:
        """
        Get workspaces that user is a member of.
        
        Args:
            user_id: User ID
            include_left: Whether to include workspaces user has left
            
        Returns:
            List of workspaces
        """
        query = (
            select(Workspace)
            .join(UserWorkspace)
            .where(
                UserWorkspace.user_id == user_id,
                Workspace.deleted_at.is_(None),
                UserWorkspace.deleted_at.is_(None)
            )
        )
        
        if not include_left:
            query = query.where(UserWorkspace.left_at.is_(None))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def slug_exists(self, slug: str, exclude_workspace_id: Optional[UUID] = None) -> bool:
        """
        Check if slug already exists.
        
        Args:
            slug: Slug to check
            exclude_workspace_id: Workspace ID to exclude from check
            
        Returns:
            True if slug exists, False otherwise
        """
        query = select(Workspace).where(
            Workspace.slug == slug,
            Workspace.deleted_at.is_(None)
        )
        
        if exclude_workspace_id:
            query = query.where(Workspace.id != exclude_workspace_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def generate_unique_slug(self, base_slug: str) -> str:
        """
        Generate a unique slug based on the base slug.
        
        Args:
            base_slug: Base slug to start with
            
        Returns:
            Unique slug
        """
        slug = base_slug
        counter = 1
        
        while await self.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def generate_invite_code(self, length: int = 8) -> str:
        """
        Generate a random invite code.
        
        Args:
            length: Length of the invite code
            
        Returns:
            Random invite code
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    async def get_member_count(self, workspace_id: UUID) -> int:
        """
        Get number of active members in workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Number of active members
        """
        query = (
            select(func.count(UserWorkspace.id))
            .where(
                UserWorkspace.workspace_id == workspace_id,
                UserWorkspace.left_at.is_(None),
                UserWorkspace.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_workspace_members(
        self,
        workspace_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get workspace members with user information.
        
        Args:
            workspace_id: Workspace ID
            limit: Maximum number of members to return
            offset: Number of members to skip
            
        Returns:
            List of member information dictionaries
        """
        query = (
            select(
                UserWorkspace.user_id,
                UserWorkspace.role,
                UserWorkspace.joined_at,
                User.username,
                User.display_name,
                User.avatar_url,
                User.last_seen_at
            )
            .join(User, UserWorkspace.user_id == User.id)
            .where(
                UserWorkspace.workspace_id == workspace_id,
                UserWorkspace.left_at.is_(None),
                UserWorkspace.deleted_at.is_(None),
                User.deleted_at.is_(None)
            )
            .order_by(UserWorkspace.joined_at)
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "user_id": row.user_id,
                "username": row.username,
                "display_name": row.display_name,
                "avatar_url": row.avatar_url,
                "role": row.role,
                "joined_at": row.joined_at,
                "last_seen_at": row.last_seen_at
            }
            for row in rows
        ]


class UserWorkspaceRepository(BaseRepository[UserWorkspace]):
    """Repository for UserWorkspace model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(UserWorkspace, db)
    
    async def get_user_workspace(
        self,
        user_id: UUID,
        workspace_id: UUID,
        include_left: bool = False
    ) -> Optional[UserWorkspace]:
        """
        Get user-workspace relationship.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            include_left: Whether to include left relationships
            
        Returns:
            UserWorkspace instance or None
        """
        query = select(UserWorkspace).where(
            UserWorkspace.user_id == user_id,
            UserWorkspace.workspace_id == workspace_id,
            UserWorkspace.deleted_at.is_(None)
        )
        
        if not include_left:
            query = query.where(UserWorkspace.left_at.is_(None))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def is_user_member(
        self,
        user_id: UUID,
        workspace_id: UUID
    ) -> bool:
        """
        Check if user is an active member of workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            
        Returns:
            True if user is active member, False otherwise
        """
        user_workspace = await self.get_user_workspace(user_id, workspace_id)
        return user_workspace is not None and user_workspace.is_active()
    
    async def get_user_role(
        self,
        user_id: UUID,
        workspace_id: UUID
    ) -> Optional[str]:
        """
        Get user's role in workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            
        Returns:
            User role or None if not a member
        """
        user_workspace = await self.get_user_workspace(user_id, workspace_id)
        return user_workspace.role if user_workspace else None
    
    async def add_user_to_workspace(
        self,
        user_id: UUID,
        workspace_id: UUID,
        role: str = "member"
    ) -> UserWorkspace:
        """
        Add user to workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            role: User role in workspace
            
        Returns:
            Created UserWorkspace instance
        """
        # Check if user was previously a member and left
        existing = await self.get_user_workspace(
            user_id, workspace_id, include_left=True
        )
        
        if existing and existing.left_at:
            # User rejoining - update existing record
            existing.left_at = None
            existing.role = role
            existing.joined_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        elif existing:
            # User already active member
            return existing
        else:
            # New member
            user_workspace = UserWorkspace(
                user_id=user_id,
                workspace_id=workspace_id,
                role=role
            )
            return await self.create(user_workspace)
    
    async def remove_user_from_workspace(
        self,
        user_id: UUID,
        workspace_id: UUID
    ) -> bool:
        """
        Remove user from workspace (soft delete).
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            
        Returns:
            True if user was removed, False if not found
        """
        user_workspace = await self.get_user_workspace(user_id, workspace_id)
        if not user_workspace:
            return False
        
        user_workspace.left_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def update_user_role(
        self,
        user_id: UUID,
        workspace_id: UUID,
        role: str
    ) -> bool:
        """
        Update user's role in workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            role: New role
            
        Returns:
            True if role was updated, False if user not found
        """
        user_workspace = await self.get_user_workspace(user_id, workspace_id)
        if not user_workspace:
            return False
        
        user_workspace.role = role
        await self.db.commit()
        return True