"""
Workspace and related models.
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Workspace(BaseModel):
    """Workspace model for organizing users and channels."""
    
    __tablename__ = "workspaces"
    
    name = Column(
        String(100),
        nullable=False,
        comment="Workspace name"
    )
    slug = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly workspace identifier"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Workspace description"
    )
    avatar_url = Column(
        Text,
        nullable=True,
        comment="URL to workspace avatar image"
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="Workspace owner user ID"
    )
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether workspace is publicly accessible"
    )
    invite_code = Column(
        String(50),
        unique=True,
        nullable=True,
        comment="Invite code for joining workspace"
    )
    max_members = Column(
        Integer,
        default=1000,
        comment="Maximum number of members allowed"
    )
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    user_workspaces = relationship("UserWorkspace", back_populates="workspace")
    channels = relationship("Channel", back_populates="workspace")
    
    def __repr__(self) -> str:
        """String representation of Workspace."""
        return f"<Workspace(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class UserWorkspace(BaseModel):
    """Association table for user-workspace relationships."""
    
    __tablename__ = "user_workspaces"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User ID"
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        comment="Workspace ID"
    )
    role = Column(
        String(20),
        nullable=False,
        default="member",
        comment="User role in workspace: owner, admin, member, guest"
    )
    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When user joined the workspace"
    )
    left_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When user left the workspace"
    )
    
    # Relationships
    user = relationship("User")
    workspace = relationship("Workspace", back_populates="user_workspaces")
    
    def is_active(self) -> bool:
        """Check if user is currently active in workspace."""
        return self.left_at is None and not self.is_deleted()
    
    def __repr__(self) -> str:
        """String representation of UserWorkspace."""
        return f"<UserWorkspace(user_id={self.user_id}, workspace_id={self.workspace_id}, role='{self.role}')>"