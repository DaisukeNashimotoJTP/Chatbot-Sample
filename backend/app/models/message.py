"""
Message and related models.
"""
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Message(BaseModel):
    """Message model for chat messages."""
    
    __tablename__ = "messages"
    
    channel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("channels.id"),
        nullable=False,
        comment="Channel where message was sent"
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User who sent the message"
    )
    content = Column(
        Text,
        nullable=True,
        comment="Message content (can be null for file-only messages)"
    )
    message_type = Column(
        String(20),
        nullable=False,
        default="text",
        comment="Message type: text, file, system"
    )
    reply_to = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.id"),
        nullable=True,
        comment="Message this is a reply to"
    )
    thread_ts = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Thread timestamp for threaded messages"
    )
    reply_count = Column(
        Integer,
        default=0,
        comment="Number of replies in thread"
    )
    is_edited = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether message has been edited"
    )
    edited_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When message was last edited"
    )
    attachments = Column(
        JSON,
        nullable=True,
        comment="File attachments metadata"
    )
    mentions = Column(
        JSON,
        nullable=True,
        comment="List of mentioned user IDs"
    )
    
    # Relationships
    channel = relationship("Channel", back_populates="messages")
    # user = relationship("User", back_populates="messages")
    # parent_message = relationship("Message", remote_side="Message.id")
    # replies = relationship("Message", remote_side="Message.reply_to")
    # reactions = relationship("MessageReaction", back_populates="message")
    
    def __repr__(self) -> str:
        """String representation of Message."""
        content_preview = (self.content[:50] + "...") if self.content and len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, user_id={self.user_id}, content='{content_preview}')>"
    
    def is_thread_reply(self) -> bool:
        """Check if this message is a reply in a thread."""
        return self.reply_to is not None


class MessageReaction(BaseModel):
    """Message reaction model."""
    
    __tablename__ = "message_reactions"
    
    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.id"),
        nullable=False,
        comment="Message being reacted to"
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User who added the reaction"
    )
    emoji = Column(
        String(10),
        nullable=False,
        comment="Reaction emoji"
    )
    
    # Relationships
    # message = relationship("Message", back_populates="reactions")
    # user = relationship("User", back_populates="message_reactions")
    
    def __repr__(self) -> str:
        return f"<MessageReaction(id={self.id}, message_id={self.message_id}, emoji={self.emoji})>"