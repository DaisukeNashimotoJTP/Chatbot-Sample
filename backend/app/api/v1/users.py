"""
User management API endpoints.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user, get_user_repository, require_user_id_match
from app.repositories.user_repository import UserRepository
from app.schemas.common import BaseResponse
from app.schemas.user import UserProfile, UserResponse, UserUpdate

router = APIRouter()


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: UUID,
    user_repository: UserRepository = Depends(get_user_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get user profile by ID.
    
    Args:
        user_id: User ID
        user_repository: User repository
        current_user: Current authenticated user
        
    Returns:
        User profile data
        
    Raises:
        HTTPException: If user not found
    """
    user = await user_repository.get_active_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: UUID,
    user_data: UserUpdate,
    user_repository: UserRepository = Depends(get_user_repository),
    current_user: UserResponse = Depends(require_user_id_match)
):
    """
    Update user profile.
    
    Args:
        user_id: User ID
        user_data: User update data
        user_repository: User repository
        current_user: Current authenticated user (must match user_id)
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If update fails
    """
    try:
        # Convert to dict and remove None values
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Update user
        updated_user = await user_repository.update(user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(updated_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        ) from e


@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user_account(
    user_id: UUID,
    user_repository: UserRepository = Depends(get_user_repository),
    current_user: UserResponse = Depends(require_user_id_match)
):
    """
    Delete user account (soft delete).
    
    Args:
        user_id: User ID
        user_repository: User repository
        current_user: Current authenticated user (must match user_id)
        
    Returns:
        Success response
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        success = await user_repository.delete(user_id, soft_delete=True)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return BaseResponse(message="Account deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        ) from e