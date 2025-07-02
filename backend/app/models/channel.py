"""
Channel and related models.
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Channel(BaseModel):
    """Channel model for organizing messages within workspaces."""
    
    __tablename__ = "channels"
    
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        comment="Workspace ID that contains this channel"
    )
    name = Column(
        String(80),
        nullable=False,
        comment="Channel name (without # prefix)"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Channel description"
    )
    type = Column(
        String(20),
        nullable=False,
        default="public",
        comment="Channel type: public, private, direct"
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User who created the channel"
    )
    is_archived = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether channel is archived"
    )
    
    # Relationships
    workspace = relationship("Workspace", back_populates="channels")
    creator = relationship("User", foreign_keys=[created_by])
    channel_members = relationship("ChannelMember", back_populates="channel")
    messages = relationship("Message", back_populates="channel")
    
    def is_active(self) -> bool:
        """Check if channel is active (not archived or deleted)."""
        return not self.is_archived and not self.is_deleted()
    
    def __repr__(self) -> str:
        """String representation of Channel."""
        return f"<Channel(id={self.id}, name='{self.name}', type='{self.type}')>"


class ChannelMember(BaseModel):
    """Association table for channel membership."""
    
    __tablename__ = "channel_members"
    
    channel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("channels.id"),
        nullable=False,
        comment="Channel ID"
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User ID"
    )
    role = Column(
        String(20),
        nullable=False,
        default="member",
        comment="User role in channel: admin, member"
    )
    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When user joined the channel"
    )
    last_read_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time user read messages in this channel"
    )
    notification_level = Column(
        String(20),
        nullable=False,
        default="all",
        comment="Notification level: all, mentions, none"
    )
    left_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When user left the channel"
    )
    
    # Relationships
    channel = relationship("Channel", back_populates="channel_members")
    user = relationship("User")
    
    def is_active(self) -> bool:
        """Check if user is currently active in channel."""
        return self.left_at is None and not self.is_deleted()
    
    def __repr__(self) -> str:
        """String representation of ChannelMember."""
        return f"<ChannelMember(user_id={self.user_id}, channel_id={self.channel_id}, role='{self.role}')>"