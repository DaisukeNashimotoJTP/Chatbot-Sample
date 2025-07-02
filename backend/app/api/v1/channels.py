"""
Channel endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models.user import User
from app.repositories.channel_repository import ChannelRepository, ChannelMemberRepository
from app.repositories.workspace_repository import UserWorkspaceRepository
from app.schemas.channel import (
    ChannelCreate,
    ChannelResponse,
    ChannelUpdate,
    ChannelInvite,
    ChannelMembersList
)
from app.services.channel_service import ChannelService

router = APIRouter()


async def get_channel_service(db: AsyncSession = Depends(get_db)) -> ChannelService:
    """Get channel service instance."""
    channel_repository = ChannelRepository(db)
    channel_member_repository = ChannelMemberRepository(db)
    user_workspace_repository = UserWorkspaceRepository(db)
    return ChannelService(
        channel_repository, 
        channel_member_repository, 
        user_workspace_repository
    )


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    workspace_id: UUID,
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Create a new channel in workspace."""
    try:
        return await channel_service.create_channel(
            workspace_id, channel_data, current_user.id
        )
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("", response_model=List[ChannelResponse])
async def get_workspace_channels(
    workspace_id: UUID,
    channel_type: Optional[str] = Query(None, regex="^(public|private)$"),
    include_archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Get channels in workspace."""
    try:
        return await channel_service.get_workspace_channels(
            workspace_id, current_user.id, channel_type, include_archived
        )
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Get channel by ID."""
    try:
        return await channel_service.get_channel(channel_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: UUID,
    channel_data: ChannelUpdate,
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Update channel."""
    try:
        return await channel_service.update_channel(
            channel_id, channel_data, current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Delete channel."""
    try:
        await channel_service.delete_channel(channel_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{channel_id}/join", response_model=ChannelResponse)
async def join_channel(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Join a channel."""
    try:
        return await channel_service.join_channel(channel_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{channel_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_channel(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Leave a channel."""
    try:
        await channel_service.leave_channel(channel_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{channel_id}/invite")
async def invite_users_to_channel(
    channel_id: UUID,
    invite_data: ChannelInvite,
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Invite users to channel."""
    try:
        results = await channel_service.invite_users_to_channel(
            channel_id, invite_data.user_ids, current_user.id
        )
        return {"results": results}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{channel_id}/members", response_model=ChannelMembersList)
async def get_channel_members(
    channel_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Get channel members."""
    try:
        return await channel_service.get_channel_members(
            channel_id, current_user.id, limit, offset
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))