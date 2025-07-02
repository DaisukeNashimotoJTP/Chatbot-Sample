"""
Custom exception classes for the application.
"""
from typing import Any, Dict, Optional


class ChatServiceException(Exception):
    """Base exception for Chat Service application."""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ChatServiceException):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.field = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details or {}
        )


class AuthenticationError(ChatServiceException):
    """Exception raised for authentication errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details=details or {}
        )


class AuthorizationError(ChatServiceException):
    """Exception raised for authorization errors."""
    
    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR", 
            details=details or {}
        )


class NotFoundError(ChatServiceException):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=message,
            code="NOT_FOUND",
            details=details or {}
        )


class ConflictError(ChatServiceException):
    """Exception raised when there's a conflict (e.g., duplicate resource)."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="CONFLICT_ERROR",
            details=details or {}
        )


class RateLimitError(ChatServiceException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.retry_after = retry_after
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            details=details or {}
        )


class FileUploadError(ChatServiceException):
    """Exception raised for file upload errors."""
    
    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="FILE_UPLOAD_ERROR",
            details=details or {}
        )


class WebSocketError(ChatServiceException):
    """Exception raised for WebSocket related errors."""
    
    def __init__(
        self,
        message: str = "WebSocket error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="WEBSOCKET_ERROR",
            details=details or {}
        )