"""
Tests for workspace functionality.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace, UserWorkspace
from app.repositories.workspace_repository import WorkspaceRepository, UserWorkspaceRepository
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


@pytest.fixture
async def workspace_service(db_session: AsyncSession) -> WorkspaceService:
    """Create workspace service for testing."""
    workspace_repository = WorkspaceRepository(db_session)
    user_workspace_repository = UserWorkspaceRepository(db_session)
    return WorkspaceService(workspace_repository, user_workspace_repository)


@pytest.fixture
async def test_workspace(db_session: AsyncSession, test_user: User) -> Workspace:
    """Create a test workspace."""
    workspace = Workspace(
        name="Test Workspace",
        slug="test-workspace",
        description="Test workspace description",
        owner_id=test_user.id,
        is_public=False,
        invite_code="testcode"
    )
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    # Add owner as member
    user_workspace = UserWorkspace(
        user_id=test_user.id,
        workspace_id=workspace.id,
        role="owner"
    )
    db_session.add(user_workspace)
    await db_session.commit()
    
    return workspace


class TestWorkspaceService:
    """Test workspace service operations."""
    
    async def test_create_workspace(
        self, 
        workspace_service: WorkspaceService, 
        test_user: User
    ):
        """Test workspace creation."""
        workspace_data = WorkspaceCreate(
            name="New Workspace",
            description="A new workspace",
            is_public=True
        )
        
        result = await workspace_service.create_workspace(workspace_data, test_user.id)
        
        assert result.name == "New Workspace"
        assert result.description == "A new workspace"
        assert result.is_public is True
        assert result.owner_id == test_user.id
        assert result.slug == "new-workspace"
        assert result.invite_code is not None
        assert result.user_role == "owner"
    
    async def test_create_workspace_with_custom_slug(
        self, 
        workspace_service: WorkspaceService, 
        test_user: User
    ):
        """Test workspace creation with custom slug."""
        workspace_data = WorkspaceCreate(
            name="Custom Workspace",
            slug="custom-slug",
            description="Custom slug workspace"
        )
        
        result = await workspace_service.create_workspace(workspace_data, test_user.id)
        
        assert result.slug == "custom-slug"
    
    async def test_get_workspace(
        self, 
        workspace_service: WorkspaceService, 
        test_workspace: Workspace, 
        test_user: User
    ):
        """Test getting workspace by ID."""
        result = await workspace_service.get_workspace(test_workspace.id, test_user.id)
        
        assert result.id == test_workspace.id
        assert result.name == test_workspace.name
        assert result.user_role == "owner"
    
    async def test_get_workspace_by_slug(
        self, 
        workspace_service: WorkspaceService, 
        test_workspace: Workspace, 
        test_user: User
    ):
        """Test getting workspace by slug."""
        result = await workspace_service.get_workspace_by_slug(
            test_workspace.slug, test_user.id
        )
        
        assert result.id == test_workspace.id
        assert result.slug == test_workspace.slug
    
    async def test_get_user_workspaces(
        self, 
        workspace_service: WorkspaceService, 
        test_workspace: Workspace, 
        test_user: User
    ):
        """Test getting user's workspaces."""
        result = await workspace_service.get_user_workspaces(test_user.id)
        
        assert len(result) == 1
        assert result[0].id == test_workspace.id
    
    async def test_update_workspace(
        self, 
        workspace_service: WorkspaceService, 
        test_workspace: Workspace, 
        test_user: User
    ):
        """Test workspace update."""
        update_data = WorkspaceUpdate(
            name="Updated Workspace",
            description="Updated description"
        )
        
        result = await workspace_service.update_workspace(
            test_workspace.id, update_data, test_user.id
        )
        
        assert result.name == "Updated Workspace"
        assert result.description == "Updated description"
    
    async def test_join_workspace_with_invite_code(
        self, 
        workspace_service: WorkspaceService, 
        test_workspace: Workspace, 
        another_user: User
    ):
        """Test joining workspace with invite code."""
        result = await workspace_service.join_workspace(
            test_workspace.invite_code, another_user.id
        )
        
        assert result.id == test_workspace.id
        assert result.user_role == "member"
    
    async def test_leave_workspace(
        self, 
        workspace_service: WorkspaceService, 
        test_workspace: Workspace, 
        another_user: User,
        db_session: AsyncSession
    ):
        """Test leaving workspace."""
        # First join the workspace
        user_workspace = UserWorkspace(
            user_id=another_user.id,
            workspace_id=test_workspace.id,
            role="member"
        )
        db_session.add(user_workspace)
        await db_session.commit()
        
        # Then leave
        result = await workspace_service.leave_workspace(
            test_workspace.id, another_user.id
        )
        
        assert result is True


class TestWorkspaceAPI:
    """Test workspace API endpoints."""
    
    async def test_create_workspace_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test POST /workspaces endpoint."""
        workspace_data = {
            "name": "API Test Workspace",
            "description": "Created via API",
            "is_public": False
        }
        
        response = await client.post(
            "/api/v1/workspaces",
            json=workspace_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Workspace"
        assert data["description"] == "Created via API"
        assert data["is_public"] is False
        assert data["slug"] == "api-test-workspace"
    
    async def test_get_user_workspaces_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test GET /workspaces endpoint."""
        response = await client.get(
            "/api/v1/workspaces",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(w["id"] == str(test_workspace.id) for w in data)
    
    async def test_get_workspace_by_id_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test GET /workspaces/{workspace_id} endpoint."""
        response = await client.get(
            f"/api/v1/workspaces/{test_workspace.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_workspace.id)
        assert data["name"] == test_workspace.name
    
    async def test_get_workspace_by_slug_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test GET /workspaces/slug/{slug} endpoint."""
        response = await client.get(
            f"/api/v1/workspaces/slug/{test_workspace.slug}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_workspace.slug
    
    async def test_update_workspace_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test PUT /workspaces/{workspace_id} endpoint."""
        update_data = {
            "name": "Updated API Workspace",
            "description": "Updated via API"
        }
        
        response = await client.put(
            f"/api/v1/workspaces/{test_workspace.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated API Workspace"
        assert data["description"] == "Updated via API"
    
    async def test_join_workspace_endpoint(
        self, 
        client: AsyncClient, 
        another_auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test POST /workspaces/join endpoint."""
        join_data = {
            "invite_code": test_workspace.invite_code
        }
        
        response = await client.post(
            "/api/v1/workspaces/join",
            json=join_data,
            headers=another_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_workspace.id)
    
    async def test_get_workspace_members_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test GET /workspaces/{workspace_id}/members endpoint."""
        response = await client.get(
            f"/api/v1/workspaces/{test_workspace.id}/members",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["members"]) >= 1
    
    async def test_workspace_authorization(
        self, 
        client: AsyncClient, 
        another_auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test that non-members can't access private workspace."""
        response = await client.get(
            f"/api/v1/workspaces/{test_workspace.id}",
            headers=another_auth_headers
        )
        
        assert response.status_code == 403