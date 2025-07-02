"""
Workspace service for business logic operations.
"""
from typing import List, Optional
from uuid import UUID
import re

from slugify import slugify

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository, UserWorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
    WorkspaceMember,
    WorkspaceMembersList
)


class WorkspaceService:
    """Service for workspace operations."""
    
    def __init__(
        self,
        workspace_repository: WorkspaceRepository,
        user_workspace_repository: UserWorkspaceRepository
    ):
        self.workspace_repository = workspace_repository
        self.user_workspace_repository = user_workspace_repository
    
    async def create_workspace(
        self,
        workspace_data: WorkspaceCreate,
        owner_id: UUID
    ) -> WorkspaceResponse:
        """
        Create a new workspace.
        
        Args:
            workspace_data: Workspace creation data
            owner_id: ID of the user creating the workspace
            
        Returns:
            Created workspace data
            
        Raises:
            ConflictError: If slug already exists
        """
        # Generate slug if not provided
        if workspace_data.slug:
            slug = workspace_data.slug
        else:
            slug = slugify(workspace_data.name, max_length=50)
        
        # Ensure slug is unique
        if await self.workspace_repository.slug_exists(slug):
            slug = await self.workspace_repository.generate_unique_slug(slug)
        
        # Generate invite code
        invite_code = self.workspace_repository.generate_invite_code()
        
        # Create workspace
        workspace = Workspace(
            name=workspace_data.name,
            slug=slug,
            description=workspace_data.description,
            avatar_url=workspace_data.avatar_url,
            owner_id=owner_id,
            is_public=workspace_data.is_public,
            invite_code=invite_code
        )
        
        created_workspace = await self.workspace_repository.create(workspace)
        
        # Add owner as admin member
        await self.user_workspace_repository.add_user_to_workspace(
            user_id=owner_id,
            workspace_id=created_workspace.id,
            role="owner"
        )
        
        return await self._build_workspace_response(created_workspace, owner_id)
    
    async def get_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID
    ) -> WorkspaceResponse:
        """
        Get workspace by ID.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID requesting the workspace
            
        Returns:
            Workspace data
            
        Raises:
            NotFoundError: If workspace not found
            AuthorizationError: If user doesn't have access
        """
        workspace = await self.workspace_repository.get(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        
        # Check if user has access
        if not workspace.is_public:
            is_member = await self.user_workspace_repository.is_user_member(
                user_id, workspace_id
            )
            if not is_member:
                raise AuthorizationError("Access denied to this workspace")
        
        return await self._build_workspace_response(workspace, user_id)
    
    async def get_workspace_by_slug(
        self,
        slug: str,
        user_id: UUID
    ) -> WorkspaceResponse:
        """
        Get workspace by slug.
        
        Args:
            slug: Workspace slug
            user_id: User ID requesting the workspace
            
        Returns:
            Workspace data
            
        Raises:
            NotFoundError: If workspace not found
            AuthorizationError: If user doesn't have access
        """
        workspace = await self.workspace_repository.get_by_slug(slug)
        if not workspace:
            raise NotFoundError("Workspace not found")
        
        # Check if user has access
        if not workspace.is_public:
            is_member = await self.user_workspace_repository.is_user_member(
                user_id, workspace.id
            )
            if not is_member:
                raise AuthorizationError("Access denied to this workspace")
        
        return await self._build_workspace_response(workspace, user_id)
    
    async def get_user_workspaces(
        self,
        user_id: UUID
    ) -> List[WorkspaceResponse]:
        """
        Get workspaces that user is a member of.
        
        Args:
            user_id: User ID
            
        Returns:
            List of workspaces
        """
        workspaces = await self.workspace_repository.get_user_workspaces(user_id)
        
        return [
            await self._build_workspace_response(workspace, user_id)
            for workspace in workspaces
        ]
    
    async def update_workspace(
        self,
        workspace_id: UUID,
        workspace_data: WorkspaceUpdate,
        user_id: UUID
    ) -> WorkspaceResponse:
        """
        Update workspace.
        
        Args:
            workspace_id: Workspace ID
            workspace_data: Update data
            user_id: User ID performing the update
            
        Returns:
            Updated workspace data
            
        Raises:
            NotFoundError: If workspace not found
            AuthorizationError: If user doesn't have permission
        """
        workspace = await self.workspace_repository.get(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        
        # Check if user has admin permissions
        user_role = await self.user_workspace_repository.get_user_role(
            user_id, workspace_id
        )
        if user_role not in ["owner", "admin"]:
            raise AuthorizationError("Insufficient permissions to update workspace")
        
        # Update workspace
        update_data = workspace_data.model_dump(exclude_unset=True)
        updated_workspace = await self.workspace_repository.update(
            workspace_id, update_data
        )
        
        return await self._build_workspace_response(updated_workspace, user_id)
    
    async def delete_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete workspace (soft delete).
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID performing the deletion
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If workspace not found
            AuthorizationError: If user is not the owner
        """
        workspace = await self.workspace_repository.get(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        
        # Only owner can delete workspace
        if workspace.owner_id != user_id:
            raise AuthorizationError("Only workspace owner can delete workspace")
        
        return await self.workspace_repository.delete(workspace_id)
    
    async def join_workspace(
        self,
        invite_code: str,
        user_id: UUID
    ) -> WorkspaceResponse:
        """
        Join workspace using invite code.
        
        Args:
            invite_code: Workspace invite code
            user_id: User ID joining the workspace
            
        Returns:
            Workspace data
            
        Raises:
            NotFoundError: If workspace not found
            ConflictError: If user is already a member
        """
        workspace = await self.workspace_repository.get_by_invite_code(invite_code)
        if not workspace:
            raise NotFoundError("Invalid invite code")
        
        # Check if user is already a member
        is_member = await self.user_workspace_repository.is_user_member(
            user_id, workspace.id
        )
        if is_member:
            raise ConflictError("User is already a member of this workspace")
        
        # Add user to workspace
        await self.user_workspace_repository.add_user_to_workspace(
            user_id=user_id,
            workspace_id=workspace.id,
            role="member"
        )
        
        return await self._build_workspace_response(workspace, user_id)
    
    async def leave_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Leave workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID leaving the workspace
            
        Returns:
            True if left successfully
            
        Raises:
            NotFoundError: If workspace not found or user not a member
            AuthorizationError: If owner tries to leave
        """
        workspace = await self.workspace_repository.get(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        
        # Owner cannot leave workspace
        if workspace.owner_id == user_id:
            raise AuthorizationError("Workspace owner cannot leave workspace")
        
        # Check if user is a member
        is_member = await self.user_workspace_repository.is_user_member(
            user_id, workspace_id
        )
        if not is_member:
            raise NotFoundError("User is not a member of this workspace")
        
        return await self.user_workspace_repository.remove_user_from_workspace(
            user_id, workspace_id
        )
    
    async def get_workspace_members(
        self,
        workspace_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> WorkspaceMembersList:
        """
        Get workspace members.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID requesting the members
            limit: Maximum number of members to return
            offset: Number of members to skip
            
        Returns:
            Workspace members list
            
        Raises:
            NotFoundError: If workspace not found
            AuthorizationError: If user doesn't have access
        """
        workspace = await self.workspace_repository.get(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        
        # Check if user has access
        is_member = await self.user_workspace_repository.is_user_member(
            user_id, workspace_id
        )
        if not is_member and not workspace.is_public:
            raise AuthorizationError("Access denied to this workspace")
        
        # Get members
        members_data = await self.workspace_repository.get_workspace_members(
            workspace_id, limit, offset
        )
        
        members = [
            WorkspaceMember(**member_data) for member_data in members_data
        ]
        
        total_count = await self.workspace_repository.get_member_count(workspace_id)
        
        return WorkspaceMembersList(members=members, total=total_count)
    
    async def _build_workspace_response(
        self,
        workspace: Workspace,
        user_id: UUID
    ) -> WorkspaceResponse:
        """
        Build workspace response with additional data.
        
        Args:
            workspace: Workspace instance
            user_id: User ID for role information
            
        Returns:
            Workspace response data
        """
        # Get member count
        member_count = await self.workspace_repository.get_member_count(workspace.id)
        
        # Get user role
        user_role = await self.user_workspace_repository.get_user_role(
            user_id, workspace.id
        )
        
        workspace_data = WorkspaceResponse.model_validate(workspace)
        workspace_data.member_count = member_count
        workspace_data.user_role = user_role
        
        return workspace_data