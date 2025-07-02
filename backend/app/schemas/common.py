"""
Common schemas and base classes.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class BaseResponse(BaseSchema):
    """Base response schema."""
    
    success: bool = True
    message: str = "Success"
    timestamp: datetime = datetime.utcnow()


class PaginationParams(BaseSchema):
    """Pagination parameters."""
    
    limit: int = 50
    offset: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit": 50,
                "offset": 0
            }
        }


class PaginationMeta(BaseSchema):
    """Pagination metadata."""
    
    total: int
    limit: int
    offset: int
    has_more: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "limit": 50,
                "offset": 0,
                "has_more": True
            }
        }


class ErrorDetail(BaseSchema):
    """Error detail schema."""
    
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    success: bool = False
    error: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed",
                    "details": [
                        {
                            "field": "email",
                            "message": "Invalid email format",
                            "code": "INVALID_EMAIL"
                        }
                    ],
                    "trace_id": "req_123456789"
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }