"""
Channel repository for database operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel, ChannelMember
from app.models.user import User
from app.repositories.base import BaseRepository


class ChannelRepository(BaseRepository[Channel]):
    """Repository for Channel model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Channel, db)
    
    async def get_workspace_channels(
        self,
        workspace_id: UUID,
        user_id: Optional[UUID] = None,
        channel_type: Optional[str] = None,
        include_archived: bool = False
    ) -> List[Channel]:
        """
        Get channels in a workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID (to filter private channels user has access to)
            channel_type: Channel type filter (public, private)
            include_archived: Whether to include archived channels
            
        Returns:
            List of channels
        """
        query = select(Channel).where(
            Channel.workspace_id == workspace_id,
            Channel.deleted_at.is_(None)
        )
        
        if not include_archived:
            query = query.where(Channel.is_archived == False)
        
        if channel_type:
            query = query.where(Channel.type == channel_type)
        
        # For private channels, only show channels user is a member of
        if user_id and channel_type != "public":
            # Join with ChannelMember to filter private channels
            query = query.outerjoin(
                ChannelMember,
                and_(
                    ChannelMember.channel_id == Channel.id,
                    ChannelMember.user_id == user_id,
                    ChannelMember.left_at.is_(None),
                    ChannelMember.deleted_at.is_(None)
                )
            ).where(
                # Include public channels and private channels user is member of
                (Channel.type == "public") | 
                (ChannelMember.id.isnot(None))
            )
        
        query = query.order_by(Channel.name)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_name_and_workspace(
        self,
        name: str,
        workspace_id: UUID
    ) -> Optional[Channel]:
        """
        Get channel by name within a workspace.
        
        Args:
            name: Channel name
            workspace_id: Workspace ID
            
        Returns:
            Channel instance or None
        """
        query = select(Channel).where(
            Channel.name == name.lower(),
            Channel.workspace_id == workspace_id,
            Channel.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def channel_name_exists(
        self,
        name: str,
        workspace_id: UUID,
        exclude_channel_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if channel name exists in workspace.
        
        Args:
            name: Channel name to check
            workspace_id: Workspace ID
            exclude_channel_id: Channel ID to exclude from check
            
        Returns:
            True if name exists, False otherwise
        """
        query = select(Channel).where(
            Channel.name == name.lower(),
            Channel.workspace_id == workspace_id,
            Channel.deleted_at.is_(None)
        )
        
        if exclude_channel_id:
            query = query.where(Channel.id != exclude_channel_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_member_count(self, channel_id: UUID) -> int:
        """
        Get number of active members in channel.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Number of active members
        """
        query = (
            select(func.count(ChannelMember.id))
            .where(
                ChannelMember.channel_id == channel_id,
                ChannelMember.left_at.is_(None),
                ChannelMember.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_channel_members(
        self,
        channel_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get channel members with user information.
        
        Args:
            channel_id: Channel ID
            limit: Maximum number of members to return
            offset: Number of members to skip
            
        Returns:
            List of member information dictionaries
        """
        query = (
            select(
                ChannelMember.user_id,
                ChannelMember.role,
                ChannelMember.joined_at,
                ChannelMember.last_read_at,
                ChannelMember.notification_level,
                User.username,
                User.display_name,
                User.avatar_url
            )
            .join(User, ChannelMember.user_id == User.id)
            .where(
                ChannelMember.channel_id == channel_id,
                ChannelMember.left_at.is_(None),
                ChannelMember.deleted_at.is_(None),
                User.deleted_at.is_(None)
            )
            .order_by(ChannelMember.joined_at)
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
                "last_read_at": row.last_read_at,
                "notification_level": row.notification_level
            }
            for row in rows
        ]


class ChannelMemberRepository(BaseRepository[ChannelMember]):
    """Repository for ChannelMember model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ChannelMember, db)
    
    async def get_channel_member(
        self,
        user_id: UUID,
        channel_id: UUID,
        include_left: bool = False
    ) -> Optional[ChannelMember]:
        """
        Get channel member relationship.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            include_left: Whether to include left relationships
            
        Returns:
            ChannelMember instance or None
        """
        query = select(ChannelMember).where(
            ChannelMember.user_id == user_id,
            ChannelMember.channel_id == channel_id,
            ChannelMember.deleted_at.is_(None)
        )
        
        if not include_left:
            query = query.where(ChannelMember.left_at.is_(None))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def is_user_member(
        self,
        user_id: UUID,
        channel_id: UUID
    ) -> bool:
        """
        Check if user is an active member of channel.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            True if user is active member, False otherwise
        """
        member = await self.get_channel_member(user_id, channel_id)
        return member is not None and member.is_active()
    
    async def get_user_role(
        self,
        user_id: UUID,
        channel_id: UUID
    ) -> Optional[str]:
        """
        Get user's role in channel.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            User role or None if not a member
        """
        member = await self.get_channel_member(user_id, channel_id)
        return member.role if member else None
    
    async def add_user_to_channel(
        self,
        user_id: UUID,
        channel_id: UUID,
        role: str = "member"
    ) -> ChannelMember:
        """
        Add user to channel.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            role: User role in channel
            
        Returns:
            Created ChannelMember instance
        """
        # Check if user was previously a member and left
        existing = await self.get_channel_member(
            user_id, channel_id, include_left=True
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
            member = ChannelMember(
                user_id=user_id,
                channel_id=channel_id,
                role=role
            )
            return await self.create(member)
    
    async def remove_user_from_channel(
        self,
        user_id: UUID,
        channel_id: UUID
    ) -> bool:
        """
        Remove user from channel (soft delete).
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            True if user was removed, False if not found
        """
        member = await self.get_channel_member(user_id, channel_id)
        if not member:
            return False
        
        member.left_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def update_user_role(
        self,
        user_id: UUID,
        channel_id: UUID,
        role: str
    ) -> bool:
        """
        Update user's role in channel.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            role: New role
            
        Returns:
            True if role was updated, False if user not found
        """
        member = await self.get_channel_member(user_id, channel_id)
        if not member:
            return False
        
        member.role = role
        await self.db.commit()
        return True
    
    async def update_last_read(
        self,
        user_id: UUID,
        channel_id: UUID
    ) -> bool:
        """
        Update user's last read timestamp for channel.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            True if updated, False if user not found
        """
        member = await self.get_channel_member(user_id, channel_id)
        if not member:
            return False
        
        member.last_read_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def get_user_channels(
        self,
        user_id: UUID,
        workspace_id: Optional[UUID] = None
    ) -> List[UUID]:
        """
        Get list of channel IDs that user is a member of.
        
        Args:
            user_id: User ID
            workspace_id: Optional workspace ID to filter by
            
        Returns:
            List of channel IDs
        """
        query = (
            select(ChannelMember.channel_id)
            .where(
                ChannelMember.user_id == user_id,
                ChannelMember.left_at.is_(None),
                ChannelMember.deleted_at.is_(None)
            )
        )
        
        if workspace_id:
            query = query.join(Channel).where(
                Channel.workspace_id == workspace_id,
                Channel.deleted_at.is_(None)
            )
        
        result = await self.db.execute(query)
        return result.scalars().all()