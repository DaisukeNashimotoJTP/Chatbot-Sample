"""
Channel service for business logic operations.
"""
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models.channel import Channel
from app.repositories.channel_repository import ChannelRepository, ChannelMemberRepository
from app.repositories.workspace_repository import UserWorkspaceRepository
from app.schemas.channel import (
    ChannelCreate,
    ChannelResponse,
    ChannelUpdate,
    ChannelMembersList
)


class ChannelService:
    """Service for channel operations."""
    
    def __init__(
        self,
        channel_repository: ChannelRepository,
        channel_member_repository: ChannelMemberRepository,
        user_workspace_repository: UserWorkspaceRepository
    ):
        self.channel_repository = channel_repository
        self.channel_member_repository = channel_member_repository
        self.user_workspace_repository = user_workspace_repository
    
    async def create_channel(
        self,
        workspace_id: UUID,
        channel_data: ChannelCreate,
        creator_id: UUID
    ) -> ChannelResponse:
        """
        Create a new channel in workspace.
        
        Args:
            workspace_id: Workspace ID
            channel_data: Channel creation data
            creator_id: ID of the user creating the channel
            
        Returns:
            Created channel data
            
        Raises:
            AuthorizationError: If user doesn't have permission
            ConflictError: If channel name already exists
        """
        # Check if user is a member of the workspace
        is_member = await self.user_workspace_repository.is_user_member(
            creator_id, workspace_id
        )
        if not is_member:
            raise AuthorizationError("User is not a member of this workspace")
        
        # Check if channel name already exists
        if await self.channel_repository.channel_name_exists(
            channel_data.name, workspace_id
        ):
            raise ConflictError(f"Channel '{channel_data.name}' already exists in this workspace")
        
        # Create channel
        channel = Channel(
            name=channel_data.name,
            description=channel_data.description,
            type=channel_data.type,
            workspace_id=workspace_id,
            created_by=creator_id
        )
        
        created_channel = await self.channel_repository.create(channel)
        
        # Add creator as admin member
        await self.channel_member_repository.add_user_to_channel(
            user_id=creator_id,
            channel_id=created_channel.id,
            role="admin"
        )
        
        return await self._build_channel_response(created_channel, creator_id)
    
    async def get_channel(
        self,
        channel_id: UUID,
        user_id: UUID
    ) -> ChannelResponse:
        """
        Get channel by ID.
        
        Args:
            channel_id: Channel ID
            user_id: User ID requesting the channel
            
        Returns:
            Channel data
            
        Raises:
            NotFoundError: If channel not found
            AuthorizationError: If user doesn't have access
        """
        channel = await self.channel_repository.get(channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        
        # Check workspace membership
        is_workspace_member = await self.user_workspace_repository.is_user_member(
            user_id, channel.workspace_id
        )
        if not is_workspace_member:
            raise AuthorizationError("Access denied to this workspace")
        
        # For private channels, check channel membership
        if channel.type == "private":
            is_channel_member = await self.channel_member_repository.is_user_member(
                user_id, channel_id
            )
            if not is_channel_member:
                raise AuthorizationError("Access denied to this private channel")
        
        return await self._build_channel_response(channel, user_id)
    
    async def get_workspace_channels(
        self,
        workspace_id: UUID,
        user_id: UUID,
        channel_type: Optional[str] = None,
        include_archived: bool = False
    ) -> List[ChannelResponse]:
        """
        Get channels in workspace that user has access to.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            channel_type: Channel type filter (public, private)
            include_archived: Whether to include archived channels
            
        Returns:
            List of channels
            
        Raises:
            AuthorizationError: If user doesn't have workspace access
        """
        # Check workspace membership
        is_workspace_member = await self.user_workspace_repository.is_user_member(
            user_id, workspace_id
        )
        if not is_workspace_member:
            raise AuthorizationError("Access denied to this workspace")
        
        # Get channels (repository handles private channel filtering)
        channels = await self.channel_repository.get_workspace_channels(
            workspace_id=workspace_id,
            user_id=user_id,
            channel_type=channel_type,
            include_archived=include_archived
        )
        
        return [
            await self._build_channel_response(channel, user_id)
            for channel in channels
        ]
    
    async def update_channel(
        self,
        channel_id: UUID,
        channel_data: ChannelUpdate,
        user_id: UUID
    ) -> ChannelResponse:
        """
        Update channel.
        
        Args:
            channel_id: Channel ID
            channel_data: Update data
            user_id: User ID performing the update
            
        Returns:
            Updated channel data
            
        Raises:
            NotFoundError: If channel not found
            AuthorizationError: If user doesn't have permission
            ConflictError: If channel name already exists
        """
        channel = await self.channel_repository.get(channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        
        # Check if user has admin permissions
        user_role = await self.channel_member_repository.get_user_role(
            user_id, channel_id
        )
        if user_role not in ["admin"]:
            # Also check workspace admin/owner permissions
            workspace_role = await self.user_workspace_repository.get_user_role(
                user_id, channel.workspace_id
            )
            if workspace_role not in ["owner", "admin"]:
                raise AuthorizationError("Insufficient permissions to update channel")
        
        # Check name uniqueness if name is being updated
        if channel_data.name and channel_data.name != channel.name:
            if await self.channel_repository.channel_name_exists(
                channel_data.name, channel.workspace_id, exclude_channel_id=channel_id
            ):
                raise ConflictError(f"Channel '{channel_data.name}' already exists in this workspace")
        
        # Update channel
        update_data = channel_data.model_dump(exclude_unset=True)
        updated_channel = await self.channel_repository.update(
            channel_id, update_data
        )
        
        return await self._build_channel_response(updated_channel, user_id)
    
    async def delete_channel(
        self,
        channel_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete channel (soft delete).
        
        Args:
            channel_id: Channel ID
            user_id: User ID performing the deletion
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If channel not found
            AuthorizationError: If user doesn't have permission
        """
        channel = await self.channel_repository.get(channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        
        # Check if user has admin permissions
        user_role = await self.channel_member_repository.get_user_role(
            user_id, channel_id
        )
        if user_role not in ["admin"]:
            # Also check workspace admin/owner permissions
            workspace_role = await self.user_workspace_repository.get_user_role(
                user_id, channel.workspace_id
            )
            if workspace_role not in ["owner", "admin"]:
                raise AuthorizationError("Insufficient permissions to delete channel")
        
        return await self.channel_repository.delete(channel_id)
    
    async def join_channel(
        self,
        channel_id: UUID,
        user_id: UUID
    ) -> ChannelResponse:
        """
        Join a channel.
        
        Args:
            channel_id: Channel ID
            user_id: User ID joining the channel
            
        Returns:
            Channel data
            
        Raises:
            NotFoundError: If channel not found
            AuthorizationError: If user doesn't have access or channel is private
            ConflictError: If user is already a member
        """
        channel = await self.channel_repository.get(channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        
        # Check workspace membership
        is_workspace_member = await self.user_workspace_repository.is_user_member(
            user_id, channel.workspace_id
        )
        if not is_workspace_member:
            raise AuthorizationError("Access denied to this workspace")
        
        # Private channels require invitation
        if channel.type == "private":
            raise AuthorizationError("Cannot join private channel without invitation")
        
        # Check if user is already a member
        is_member = await self.channel_member_repository.is_user_member(
            user_id, channel_id
        )
        if is_member:
            raise ConflictError("User is already a member of this channel")
        
        # Add user to channel
        await self.channel_member_repository.add_user_to_channel(
            user_id=user_id,
            channel_id=channel_id,
            role="member"
        )
        
        return await self._build_channel_response(channel, user_id)
    
    async def leave_channel(
        self,
        channel_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Leave a channel.
        
        Args:
            channel_id: Channel ID
            user_id: User ID leaving the channel
            
        Returns:
            True if left successfully
            
        Raises:
            NotFoundError: If channel not found or user not a member
        """
        channel = await self.channel_repository.get(channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        
        # Check if user is a member
        is_member = await self.channel_member_repository.is_user_member(
            user_id, channel_id
        )
        if not is_member:
            raise NotFoundError("User is not a member of this channel")
        
        return await self.channel_member_repository.remove_user_from_channel(
            user_id, channel_id
        )
    
    async def invite_users_to_channel(
        self,
        channel_id: UUID,
        user_ids: List[UUID],
        inviter_id: UUID
    ) -> List[str]:
        """
        Invite users to a channel.
        
        Args:
            channel_id: Channel ID
            user_ids: List of user IDs to invite
            inviter_id: User ID performing the invitation
            
        Returns:
            List of results for each invitation
            
        Raises:
            NotFoundError: If channel not found
            AuthorizationError: If user doesn't have permission
        """
        channel = await self.channel_repository.get(channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        
        # Check if inviter has permission
        inviter_role = await self.channel_member_repository.get_user_role(
            inviter_id, channel_id
        )
        if not inviter_role:
            raise AuthorizationError("User is not a member of this channel")
        
        results = []
        for user_id in user_ids:
            try:
                # Check if user is workspace member
                is_workspace_member = await self.user_workspace_repository.is_user_member(
                    user_id, channel.workspace_id
                )
                if not is_workspace_member:
                    results.append(f"User {user_id}: Not a workspace member")
                    continue
                
                # Check if already a member
                is_member = await self.channel_member_repository.is_user_member(
                    user_id, channel_id
                )
                if is_member:
                    results.append(f"User {user_id}: Already a member")
                    continue
                
                # Add to channel
                await self.channel_member_repository.add_user_to_channel(
                    user_id=user_id,
                    channel_id=channel_id,
                    role="member"
                )
                results.append(f"User {user_id}: Successfully invited")
                
            except Exception as e:
                results.append(f"User {user_id}: Error - {str(e)}")
        
        return results
    
    async def get_channel_members(
        self,
        channel_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> ChannelMembersList:
        """
        Get channel members.
        
        Args:
            channel_id: Channel ID
            user_id: User ID requesting the members
            limit: Maximum number of members to return
            offset: Number of members to skip
            
        Returns:
            Channel members list
            
        Raises:
            NotFoundError: If channel not found
            AuthorizationError: If user doesn't have access
        """
        channel = await self.channel_repository.get(channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        
        # Check access
        if channel.type == "private":
            is_member = await self.channel_member_repository.is_user_member(
                user_id, channel_id
            )
            if not is_member:
                raise AuthorizationError("Access denied to this private channel")
        else:
            # For public channels, check workspace membership
            is_workspace_member = await self.user_workspace_repository.is_user_member(
                user_id, channel.workspace_id
            )
            if not is_workspace_member:
                raise AuthorizationError("Access denied to this workspace")
        
        # Get members
        members_data = await self.channel_repository.get_channel_members(
            channel_id, limit, offset
        )
        
        from app.schemas.channel import ChannelMemberResponse
        members = [
            ChannelMemberResponse(**member_data) for member_data in members_data
        ]
        
        total_count = await self.channel_repository.get_member_count(channel_id)
        
        return ChannelMembersList(members=members, total=total_count)
    
    async def _build_channel_response(
        self,
        channel: Channel,
        user_id: UUID
    ) -> ChannelResponse:
        """
        Build channel response with additional data.
        
        Args:
            channel: Channel instance
            user_id: User ID for role information
            
        Returns:
            Channel response data
        """
        # Get member count
        member_count = await self.channel_repository.get_member_count(channel.id)
        
        # Get user role
        user_role = await self.channel_member_repository.get_user_role(
            user_id, channel.id
        )
        
        channel_data = ChannelResponse.model_validate(channel)
        channel_data.member_count = member_count
        channel_data.user_role = user_role
        
        return channel_data