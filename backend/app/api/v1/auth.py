"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.api.deps import get_auth_service, get_current_active_user
from app.core.exceptions import AuthenticationError, ConflictError
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    PasswordChangeRequest,
)
from app.schemas.common import BaseResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        auth_service: Authentication service
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        user = await auth_service.register_user(user_data)
        return user
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        ) from e


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return access tokens.
    
    Args:
        login_data: Login credentials
        auth_service: Authentication service
        
    Returns:
        Login response with user data and tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        login_response = await auth_service.authenticate_user(
            login_data.email,
            login_data.password
        )
        return login_response
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        ) from e


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token data
        auth_service: Authentication service
        
    Returns:
        New token response
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        token_response = await auth_service.refresh_token(refresh_data.refresh_token)
        return token_response
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return current_user


@router.post("/logout", response_model=BaseResponse)
async def logout(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Logout user (client-side token invalidation).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success response
        
    Note:
        Since we're using stateless JWT tokens, actual logout is handled
        client-side by removing the token. In a production system, you might
        want to implement a token blacklist for immediate invalidation.
    """
    return BaseResponse(message="Logged out successfully")


@router.post("/change-password", response_model=BaseResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change user's password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        Success response
        
    Raises:
        HTTPException: If password change fails
    """
    try:
        await auth_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        return BaseResponse(message="Password changed successfully")
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        ) from e


@router.post("/verify-email", response_model=BaseResponse)
async def verify_email(
    current_user: UserResponse = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify user's email address.
    
    Args:
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        Success response
        
    Note:
        In a real implementation, this would be called with a verification
        token sent via email. For MVP simplicity, we allow direct verification.
    """
    try:
        await auth_service.verify_email(current_user.id)
        return BaseResponse(message="Email verified successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        ) from e