"""
Message service for business logic operations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from app.models.message import Message, MessageReaction
from app.repositories.message_repository import MessageRepository, MessageReactionRepository
from app.repositories.channel_repository import ChannelMemberRepository
from app.schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageList,
    MessageReactionCreate,
    MessageReactionResponse,
    ThreadResponse
)


class MessageService:
    """Service for message operations."""
    
    def __init__(
        self,
        message_repository: MessageRepository,
        message_reaction_repository: MessageReactionRepository,
        channel_member_repository: ChannelMemberRepository
    ):
        self.message_repository = message_repository
        self.message_reaction_repository = message_reaction_repository
        self.channel_member_repository = channel_member_repository
    
    async def create_message(
        self,
        channel_id: UUID,
        message_data: MessageCreate,
        sender_id: UUID
    ) -> MessageResponse:
        """
        Create a new message in channel.
        
        Args:
            channel_id: Channel ID
            message_data: Message creation data
            sender_id: ID of the user sending the message
            
        Returns:
            Created message data
            
        Raises:
            AuthorizationError: If user doesn't have permission
            NotFoundError: If reply_to message not found
        """
        # Check if user is a member of the channel
        is_member = await self.channel_member_repository.is_user_member(
            sender_id, channel_id
        )
        if not is_member:
            raise AuthorizationError("User is not a member of this channel")
        
        # Validate reply_to message if provided
        thread_ts = None
        if message_data.reply_to:
            parent_message = await self.message_repository.get(message_data.reply_to)
            if not parent_message:
                raise NotFoundError("Parent message not found")
            
            if parent_message.channel_id != channel_id:
                raise ValidationError("Cannot reply to message from different channel")
            
            # Set thread timestamp
            thread_ts = parent_message.thread_ts or parent_message.created_at
        
        # Create message
        message = Message(
            channel_id=channel_id,
            user_id=sender_id,
            content=message_data.content,
            message_type=message_data.message_type,
            reply_to=message_data.reply_to,
            thread_ts=thread_ts,
            attachments=message_data.attachments,
            mentions=message_data.mentions
        )
        
        created_message = await self.message_repository.create(message)
        
        # Update reply count if this is a thread reply
        if message_data.reply_to:
            await self.message_repository.increment_reply_count(message_data.reply_to)
        
        # Get message with user info for response
        message_data = await self.message_repository.get_message_with_user(created_message.id)
        if not message_data:
            raise NotFoundError("Created message not found")
        
        return await self._build_message_response(message_data, sender_id)
    
    async def get_message(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> MessageResponse:
        """
        Get message by ID.
        
        Args:
            message_id: Message ID
            user_id: User ID requesting the message
            
        Returns:
            Message data
            
        Raises:
            NotFoundError: If message not found
            AuthorizationError: If user doesn't have access
        """
        message_data = await self.message_repository.get_message_with_user(message_id)
        if not message_data:
            raise NotFoundError("Message not found")
        
        # Check if user has access to the channel
        is_member = await self.channel_member_repository.is_user_member(
            user_id, message_data["channel_id"]
        )
        if not is_member:
            raise AuthorizationError("Access denied to this channel")
        
        return await self._build_message_response(message_data, user_id)
    
    async def get_channel_messages(
        self,
        channel_id: UUID,
        user_id: UUID,
        limit: int = 50,
        before: Optional[UUID] = None,
        after: Optional[UUID] = None,
        include_threads: bool = False
    ) -> MessageList:
        """
        Get messages in a channel.
        
        Args:
            channel_id: Channel ID
            user_id: User ID
            limit: Maximum number of messages to return
            before: Get messages before this message ID
            after: Get messages after this message ID
            include_threads: Whether to include thread replies
            
        Returns:
            List of messages
            
        Raises:
            AuthorizationError: If user doesn't have access
        """
        # Check if user has access to the channel
        is_member = await self.channel_member_repository.is_user_member(
            user_id, channel_id
        )
        if not is_member:
            raise AuthorizationError("Access denied to this channel")
        
        # Get messages
        messages_data = await self.message_repository.get_channel_messages(
            channel_id=channel_id,
            limit=limit + 1,  # Get one extra to check if there are more
            before=before,
            after=after,
            include_threads=include_threads
        )
        
        # Check if there are more messages
        has_more = len(messages_data) > limit
        if has_more:
            messages_data = messages_data[:limit]
        
        messages = []
        for message_data in messages_data:
            message_response = await self._build_message_response(message_data, user_id)
            messages.append(message_response)
        
        return MessageList(
            messages=messages,
            total=len(messages),  # In a real implementation, you'd want a separate count query
            has_more=has_more
        )
    
    async def get_thread_messages(
        self,
        parent_message_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> ThreadResponse:
        """
        Get messages in a thread.
        
        Args:
            parent_message_id: Parent message ID
            user_id: User ID
            limit: Maximum number of replies to return
            offset: Number of replies to skip
            
        Returns:
            Thread data with parent message and replies
            
        Raises:
            NotFoundError: If parent message not found
            AuthorizationError: If user doesn't have access
        """
        # Get parent message
        parent_data = await self.message_repository.get_message_with_user(parent_message_id)
        if not parent_data:
            raise NotFoundError("Parent message not found")
        
        # Check if user has access to the channel
        is_member = await self.channel_member_repository.is_user_member(
            user_id, parent_data["channel_id"]
        )
        if not is_member:
            raise AuthorizationError("Access denied to this channel")
        
        # Get thread replies
        replies_data = await self.message_repository.get_thread_messages(
            parent_message_id, limit, offset
        )
        
        parent_message = await self._build_message_response(parent_data, user_id)
        replies = []
        for reply_data in replies_data:
            reply_response = await self._build_message_response(reply_data, user_id)
            replies.append(reply_response)
        
        return ThreadResponse(
            parent_message=parent_message,
            replies=replies,
            total_replies=parent_data["reply_count"]
        )
    
    async def update_message(
        self,
        message_id: UUID,
        message_data: MessageUpdate,
        user_id: UUID
    ) -> MessageResponse:
        """
        Update message content.
        
        Args:
            message_id: Message ID
            message_data: Update data
            user_id: User ID performing the update
            
        Returns:
            Updated message data
            
        Raises:
            NotFoundError: If message not found
            AuthorizationError: If user doesn't have permission
        """
        message = await self.message_repository.get(message_id)
        if not message:
            raise NotFoundError("Message not found")
        
        # Only the message sender can edit the message
        if message.user_id != user_id:
            raise AuthorizationError("Only the message sender can edit this message")
        
        # Update message
        message.content = message_data.content
        message.is_edited = True
        message.edited_at = datetime.utcnow()
        
        updated_message = await self.message_repository.update(
            message_id, {
                "content": message_data.content,
                "is_edited": True,
                "edited_at": datetime.utcnow()
            }
        )
        
        # Get updated message with user info
        message_data_response = await self.message_repository.get_message_with_user(message_id)
        if not message_data_response:
            raise NotFoundError("Updated message not found")
        
        return await self._build_message_response(message_data_response, user_id)
    
    async def delete_message(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete message (soft delete).
        
        Args:
            message_id: Message ID
            user_id: User ID performing the deletion
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If message not found
            AuthorizationError: If user doesn't have permission
        """
        message = await self.message_repository.get(message_id)
        if not message:
            raise NotFoundError("Message not found")
        
        # Only the message sender can delete the message
        # TODO: Also allow channel admins and workspace admins
        if message.user_id != user_id:
            raise AuthorizationError("Only the message sender can delete this message")
        
        # Update reply count if this was a thread reply
        if message.reply_to:
            await self.message_repository.decrement_reply_count(message.reply_to)
        
        return await self.message_repository.delete(message_id)
    
    async def add_reaction(
        self,
        message_id: UUID,
        reaction_data: MessageReactionCreate,
        user_id: UUID
    ) -> MessageReactionResponse:
        """
        Add reaction to message.
        
        Args:
            message_id: Message ID
            reaction_data: Reaction data
            user_id: User ID adding the reaction
            
        Returns:
            Created reaction data
            
        Raises:
            NotFoundError: If message not found
            AuthorizationError: If user doesn't have access
        """
        message_data = await self.message_repository.get_message_with_user(message_id)
        if not message_data:
            raise NotFoundError("Message not found")
        
        # Check if user has access to the channel
        is_member = await self.channel_member_repository.is_user_member(
            user_id, message_data["channel_id"]
        )
        if not is_member:
            raise AuthorizationError("Access denied to this channel")
        
        # Check if reaction already exists
        existing_reaction = await self.message_reaction_repository.get_user_reaction(
            message_id, user_id, reaction_data.emoji
        )
        
        if existing_reaction:
            # Remove existing reaction (toggle off)
            await self.message_reaction_repository.delete(existing_reaction.id)
            raise ValidationError("Reaction removed")
        
        # Create new reaction
        reaction = MessageReaction(
            message_id=message_id,
            user_id=user_id,
            emoji=reaction_data.emoji
        )
        
        created_reaction = await self.message_reaction_repository.create(reaction)
        
        # Get reaction with user info
        reactions_data = await self.message_reaction_repository.get_message_reactions(message_id)
        reaction_data = next(
            (r for r in reactions_data if r["id"] == created_reaction.id),
            None
        )
        
        if not reaction_data:
            raise NotFoundError("Created reaction not found")
        
        return MessageReactionResponse(**reaction_data)
    
    async def remove_reaction(
        self,
        message_id: UUID,
        emoji: str,
        user_id: UUID
    ) -> bool:
        """
        Remove reaction from message.
        
        Args:
            message_id: Message ID
            emoji: Reaction emoji
            user_id: User ID removing the reaction
            
        Returns:
            True if removed successfully
            
        Raises:
            NotFoundError: If message or reaction not found
            AuthorizationError: If user doesn't have access
        """
        message_data = await self.message_repository.get_message_with_user(message_id)
        if not message_data:
            raise NotFoundError("Message not found")
        
        # Check if user has access to the channel
        is_member = await self.channel_member_repository.is_user_member(
            user_id, message_data["channel_id"]
        )
        if not is_member:
            raise AuthorizationError("Access denied to this channel")
        
        # Find and remove reaction
        reaction = await self.message_reaction_repository.get_user_reaction(
            message_id, user_id, emoji
        )
        
        if not reaction:
            raise NotFoundError("Reaction not found")
        
        return await self.message_reaction_repository.delete(reaction.id)
    
    async def get_message_reactions(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> List[MessageReactionResponse]:
        """
        Get reactions for a message.
        
        Args:
            message_id: Message ID
            user_id: User ID requesting reactions
            
        Returns:
            List of reactions
            
        Raises:
            NotFoundError: If message not found
            AuthorizationError: If user doesn't have access
        """
        message_data = await self.message_repository.get_message_with_user(message_id)
        if not message_data:
            raise NotFoundError("Message not found")
        
        # Check if user has access to the channel
        is_member = await self.channel_member_repository.is_user_member(
            user_id, message_data["channel_id"]
        )
        if not is_member:
            raise AuthorizationError("Access denied to this channel")
        
        reactions_data = await self.message_reaction_repository.get_message_reactions(message_id)
        
        return [MessageReactionResponse(**reaction_data) for reaction_data in reactions_data]
    
    async def _build_message_response(
        self,
        message_data: Dict[str, Any],
        user_id: UUID
    ) -> MessageResponse:
        """
        Build message response with additional data.
        
        Args:
            message_data: Message data from repository
            user_id: User ID for reaction information
            
        Returns:
            Message response data
        """
        # Get reaction data
        reaction_counts = await self.message_reaction_repository.get_reaction_counts(
            message_data["id"]
        )
        user_reactions = await self.message_reaction_repository.get_user_reactions(
            message_data["id"], user_id
        )
        
        response_data = MessageResponse.model_validate(message_data)
        response_data.reaction_counts = reaction_counts if reaction_counts else None
        response_data.user_reactions = user_reactions if user_reactions else None
        
        return response_data