"""
Message endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.user import User
from app.repositories.message_repository import MessageRepository, MessageReactionRepository
from app.repositories.channel_repository import ChannelRepository, ChannelMemberRepository
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageUpdate,
    MessageList
)
from app.services.message_service import MessageService

router = APIRouter()


async def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    """Get message service instance."""
    message_repository = MessageRepository(db)
    message_reaction_repository = MessageReactionRepository(db)
    channel_member_repository = ChannelMemberRepository(db)
    return MessageService(
        message_repository,
        message_reaction_repository, 
        channel_member_repository
    )


@router.get("/channels/{channel_id}/messages", response_model=MessageList)
async def get_channel_messages(
    channel_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    before: Optional[UUID] = Query(None),
    after: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """Get messages in a channel."""
    try:
        return await message_service.get_channel_messages(
            channel_id, current_user.id, limit, before, after
        )
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/channels/{channel_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    channel_id: UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """Create a new message in channel."""
    try:
        return await message_service.create_message(
            channel_id, message_data, current_user.id
        )
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """Get message by ID."""
    try:
        return await message_service.get_message(message_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: UUID,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """Update message."""
    try:
        return await message_service.update_message(
            message_id, message_data, current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """Delete message."""
    try:
        await message_service.delete_message(message_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/messages/{message_id}/thread", response_model=List[MessageResponse])
async def get_thread_messages(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """Get thread messages for a parent message."""
    try:
        return await message_service.get_thread_messages(message_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
