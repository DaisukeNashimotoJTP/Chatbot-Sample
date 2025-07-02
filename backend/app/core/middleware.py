"""
Custom middleware for the application.
"""
import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app.core.exceptions import ChatServiceException

logger = structlog.get_logger()


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to log requests and responses.
    """
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=round(process_time, 4),
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as exc:
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log error
        logger.error(
            "Request failed",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            process_time=round(process_time, 4),
            error=str(exc),
            exc_info=True,
        )
        
        raise


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to handle exceptions and return structured error responses.
    """
    try:
        response = await call_next(request)
        return response
        
    except ChatServiceException as exc:
        # Handle custom application exceptions
        error_response = {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "trace_id": getattr(request.state, "request_id", None),
            },
            "timestamp": time.time(),
        }
        
        # Map exception types to HTTP status codes
        status_map = {
            "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
            "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
            "NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "CONFLICT_ERROR": status.HTTP_409_CONFLICT,
            "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
            "FILE_UPLOAD_ERROR": status.HTTP_400_BAD_REQUEST,
            "WEBSOCKET_ERROR": status.HTTP_400_BAD_REQUEST,
        }
        
        status_code = status_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )
        
    except Exception as exc:
        # Handle unexpected exceptions
        logger.error(
            "Unhandled exception",
            error=str(exc),
            exc_info=True,
            request_id=getattr(request.state, "request_id", None),
        )
        
        error_response = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
                "trace_id": getattr(request.state, "request_id", None),
            },
            "timestamp": time.time(),
        }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )