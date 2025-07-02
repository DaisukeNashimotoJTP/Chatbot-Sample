"""
File storage model.
"""
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class File(BaseModel):
    """File model for uploaded files."""
    
    __tablename__ = "files"
    
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        comment="Workspace where file was uploaded"
    )
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User who uploaded the file"
    )
    filename = Column(
        String(255),
        nullable=False,
        comment="Original filename"
    )
    file_size = Column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )
    mime_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of the file"
    )
    storage_path = Column(
        Text,
        nullable=False,
        comment="Storage path or S3 key"
    )
    thumbnail_path = Column(
        Text,
        nullable=True,
        comment="Path to thumbnail image (for images/videos)"
    )
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether file is publicly accessible"
    )
    
    # Relationships
    workspace = relationship("Workspace")
    uploader = relationship("User")
    
    def __repr__(self) -> str:
        """String representation of File."""
        return f"<File(id={self.id}, filename='{self.filename}', size={self.file_size})>"