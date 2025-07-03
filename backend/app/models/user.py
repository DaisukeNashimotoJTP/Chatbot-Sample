"""
User model definition.
"""
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for storing user account information."""
    
    __tablename__ = "users"
    
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique username for the user"
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User's email address"
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password"
    )
    display_name = Column(
        String(100),
        nullable=False,
        comment="Display name for the user"
    )
    avatar_url = Column(
        Text,
        nullable=True,
        comment="URL to user's avatar image"
    )
    status = Column(
        String(20),
        nullable=False,
        default="active",
        comment="User status: active, inactive, suspended"
    )
    timezone = Column(
        String(50),
        default="UTC",
        comment="User's timezone"
    )
    last_seen_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time user was seen online"
    )
    email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether user's email is verified"
    )
    
    # Relationships (will be added as we implement other models)
    # user_workspaces = relationship("UserWorkspace", back_populates="user")
    # messages = relationship("Message", back_populates="user")
    # message_reactions = relationship("MessageReaction", back_populates="user")
    # files = relationship("File", back_populates="uploaded_by_user")
    
    def is_active(self) -> bool:
        """Check if user is active and not deleted."""
        return (
            self.status == "active" 
            and not self.is_deleted()
        )
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"