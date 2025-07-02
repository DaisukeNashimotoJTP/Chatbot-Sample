"""
Message repository for database operations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message, MessageReaction
from app.models.user import User
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Message, db)
    
    async def get_channel_messages(
        self,
        channel_id: UUID,
        limit: int = 50,
        before: Optional[UUID] = None,
        after: Optional[UUID] = None,
        include_threads: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get messages in a channel with user information.
        
        Args:
            channel_id: Channel ID
            limit: Maximum number of messages to return
            before: Get messages before this message ID
            after: Get messages after this message ID
            include_threads: Whether to include thread replies
            
        Returns:
            List of message data with user information
        """
        query = (
            select(
                Message.id,
                Message.content,
                Message.message_type,
                Message.reply_to,
                Message.thread_ts,
                Message.reply_count,
                Message.is_edited,
                Message.edited_at,
                Message.attachments,
                Message.mentions,
                Message.created_at,
                Message.updated_at,
                Message.user_id,
                User.username.label("user_username"),
                User.display_name.label("user_display_name"),
                User.avatar_url.label("user_avatar_url")
            )
            .join(User, Message.user_id == User.id)
            .where(
                Message.channel_id == channel_id,
                Message.deleted_at.is_(None),
                User.deleted_at.is_(None)
            )
        )
        
        # Filter thread replies if not requested
        if not include_threads:
            query = query.where(Message.reply_to.is_(None))
        
        # Pagination
        if before:
            before_message = await self.get(before)
            if before_message:
                query = query.where(Message.created_at < before_message.created_at)
        
        if after:
            after_message = await self.get(after)
            if after_message:
                query = query.where(Message.created_at > after_message.created_at)
        
        query = query.order_by(desc(Message.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "id": row.id,
                "channel_id": channel_id,
                "user_id": row.user_id,
                "content": row.content,
                "message_type": row.message_type,
                "reply_to": row.reply_to,
                "thread_ts": row.thread_ts,
                "reply_count": row.reply_count,
                "is_edited": row.is_edited,
                "edited_at": row.edited_at,
                "attachments": row.attachments,
                "mentions": row.mentions,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "user_username": row.user_username,
                "user_display_name": row.user_display_name,
                "user_avatar_url": row.user_avatar_url
            }
            for row in rows
        ]
    
    async def get_thread_messages(
        self,
        parent_message_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get messages in a thread.
        
        Args:
            parent_message_id: Parent message ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of thread message data with user information
        """
        query = (
            select(
                Message.id,
                Message.content,
                Message.message_type,
                Message.reply_to,
                Message.thread_ts,
                Message.reply_count,
                Message.is_edited,
                Message.edited_at,
                Message.attachments,
                Message.mentions,
                Message.created_at,
                Message.updated_at,
                Message.user_id,
                User.username.label("user_username"),
                User.display_name.label("user_display_name"),
                User.avatar_url.label("user_avatar_url")
            )
            .join(User, Message.user_id == User.id)
            .where(
                Message.reply_to == parent_message_id,
                Message.deleted_at.is_(None),
                User.deleted_at.is_(None)
            )
            .order_by(Message.created_at)
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "id": row.id,
                "user_id": row.user_id,
                "content": row.content,
                "message_type": row.message_type,
                "reply_to": row.reply_to,
                "thread_ts": row.thread_ts,
                "reply_count": row.reply_count,
                "is_edited": row.is_edited,
                "edited_at": row.edited_at,
                "attachments": row.attachments,
                "mentions": row.mentions,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "user_username": row.user_username,
                "user_display_name": row.user_display_name,
                "user_avatar_url": row.user_avatar_url
            }
            for row in rows
        ]
    
    async def get_message_with_user(self, message_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get message with user information.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message data with user information or None
        """
        query = (
            select(
                Message.id,
                Message.channel_id,
                Message.content,
                Message.message_type,
                Message.reply_to,
                Message.thread_ts,
                Message.reply_count,
                Message.is_edited,
                Message.edited_at,
                Message.attachments,
                Message.mentions,
                Message.created_at,
                Message.updated_at,
                Message.user_id,
                User.username.label("user_username"),
                User.display_name.label("user_display_name"),
                User.avatar_url.label("user_avatar_url")
            )
            .join(User, Message.user_id == User.id)
            .where(
                Message.id == message_id,
                Message.deleted_at.is_(None),
                User.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        return {
            "id": row.id,
            "channel_id": row.channel_id,
            "user_id": row.user_id,
            "content": row.content,
            "message_type": row.message_type,
            "reply_to": row.reply_to,
            "thread_ts": row.thread_ts,
            "reply_count": row.reply_count,
            "is_edited": row.is_edited,
            "edited_at": row.edited_at,
            "attachments": row.attachments,
            "mentions": row.mentions,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "user_username": row.user_username,
            "user_display_name": row.user_display_name,
            "user_avatar_url": row.user_avatar_url
        }
    
    async def search_messages(
        self,
        channel_id: UUID,
        query_text: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search messages in a channel.
        
        Args:
            channel_id: Channel ID
            query_text: Search query
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of matching message data
        """
        query = (
            select(
                Message.id,
                Message.content,
                Message.message_type,
                Message.reply_to,
                Message.thread_ts,
                Message.reply_count,
                Message.is_edited,
                Message.edited_at,
                Message.attachments,
                Message.mentions,
                Message.created_at,
                Message.updated_at,
                Message.user_id,
                User.username.label("user_username"),
                User.display_name.label("user_display_name"),
                User.avatar_url.label("user_avatar_url")
            )
            .join(User, Message.user_id == User.id)
            .where(
                Message.channel_id == channel_id,
                Message.content.ilike(f"%{query_text}%"),
                Message.deleted_at.is_(None),
                User.deleted_at.is_(None)
            )
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "id": row.id,
                "channel_id": channel_id,
                "user_id": row.user_id,
                "content": row.content,
                "message_type": row.message_type,
                "reply_to": row.reply_to,
                "thread_ts": row.thread_ts,
                "reply_count": row.reply_count,
                "is_edited": row.is_edited,
                "edited_at": row.edited_at,
                "attachments": row.attachments,
                "mentions": row.mentions,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "user_username": row.user_username,
                "user_display_name": row.user_display_name,
                "user_avatar_url": row.user_avatar_url
            }
            for row in rows
        ]
    
    async def increment_reply_count(self, message_id: UUID) -> bool:
        """
        Increment reply count for a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            True if updated successfully
        """
        message = await self.get(message_id)
        if not message:
            return False
        
        message.reply_count = (message.reply_count or 0) + 1
        await self.db.commit()
        return True
    
    async def decrement_reply_count(self, message_id: UUID) -> bool:
        """
        Decrement reply count for a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            True if updated successfully
        """
        message = await self.get(message_id)
        if not message:
            return False
        
        message.reply_count = max((message.reply_count or 0) - 1, 0)
        await self.db.commit()
        return True


class MessageReactionRepository(BaseRepository[MessageReaction]):
    """Repository for MessageReaction model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(MessageReaction, db)
    
    async def get_message_reactions(
        self,
        message_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get reactions for a message with user information.
        
        Args:
            message_id: Message ID
            
        Returns:
            List of reaction data with user information
        """
        query = (
            select(
                MessageReaction.id,
                MessageReaction.message_id,
                MessageReaction.user_id,
                MessageReaction.emoji,
                MessageReaction.created_at,
                User.username.label("user_username"),
                User.display_name.label("user_display_name"),
                User.avatar_url.label("user_avatar_url")
            )
            .join(User, MessageReaction.user_id == User.id)
            .where(
                MessageReaction.message_id == message_id,
                MessageReaction.deleted_at.is_(None),
                User.deleted_at.is_(None)
            )
            .order_by(MessageReaction.created_at)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "id": row.id,
                "message_id": row.message_id,
                "user_id": row.user_id,
                "emoji": row.emoji,
                "created_at": row.created_at,
                "user_username": row.user_username,
                "user_display_name": row.user_display_name,
                "user_avatar_url": row.user_avatar_url
            }
            for row in rows
        ]
    
    async def get_user_reaction(
        self,
        message_id: UUID,
        user_id: UUID,
        emoji: str
    ) -> Optional[MessageReaction]:
        """
        Get specific user reaction to a message.
        
        Args:
            message_id: Message ID
            user_id: User ID
            emoji: Reaction emoji
            
        Returns:
            MessageReaction instance or None
        """
        query = select(MessageReaction).where(
            MessageReaction.message_id == message_id,
            MessageReaction.user_id == user_id,
            MessageReaction.emoji == emoji,
            MessageReaction.deleted_at.is_(None)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_reaction_counts(
        self,
        message_id: UUID
    ) -> Dict[str, int]:
        """
        Get reaction counts for a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Dictionary mapping emoji to count
        """
        query = (
            select(
                MessageReaction.emoji,
                func.count(MessageReaction.id).label("count")
            )
            .where(
                MessageReaction.message_id == message_id,
                MessageReaction.deleted_at.is_(None)
            )
            .group_by(MessageReaction.emoji)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return {row.emoji: row.count for row in rows}
    
    async def get_user_reactions(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> List[str]:
        """
        Get user's reactions to a message.
        
        Args:
            message_id: Message ID
            user_id: User ID
            
        Returns:
            List of emoji strings
        """
        query = select(MessageReaction.emoji).where(
            MessageReaction.message_id == message_id,
            MessageReaction.user_id == user_id,
            MessageReaction.deleted_at.is_(None)
        )
        
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]