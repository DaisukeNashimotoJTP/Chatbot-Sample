"""
Tests for channel functionality.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace, UserWorkspace
from app.models.channel import Channel, ChannelMember
from app.repositories.channel_repository import ChannelRepository, ChannelMemberRepository
from app.repositories.workspace_repository import UserWorkspaceRepository
from app.services.channel_service import ChannelService
from app.schemas.channel import ChannelCreate, ChannelUpdate


@pytest.fixture
async def channel_service(db_session: AsyncSession) -> ChannelService:
    """Create channel service for testing."""
    channel_repository = ChannelRepository(db_session)
    channel_member_repository = ChannelMemberRepository(db_session)
    user_workspace_repository = UserWorkspaceRepository(db_session)
    return ChannelService(
        channel_repository, 
        channel_member_repository, 
        user_workspace_repository
    )


@pytest.fixture
async def test_channel(
    db_session: AsyncSession, 
    test_workspace: Workspace, 
    test_user: User
) -> Channel:
    """Create a test channel."""
    channel = Channel(
        name="general",
        description="General discussion channel",
        type="public",
        workspace_id=test_workspace.id,
        created_by=test_user.id
    )
    db_session.add(channel)
    await db_session.commit()
    await db_session.refresh(channel)
    
    # Add creator as admin member
    channel_member = ChannelMember(
        user_id=test_user.id,
        channel_id=channel.id,
        role="admin"
    )
    db_session.add(channel_member)
    await db_session.commit()
    
    return channel


@pytest.fixture
async def private_channel(
    db_session: AsyncSession, 
    test_workspace: Workspace, 
    test_user: User
) -> Channel:
    """Create a private test channel."""
    channel = Channel(
        name="private-channel",
        description="Private channel",
        type="private",
        workspace_id=test_workspace.id,
        created_by=test_user.id
    )
    db_session.add(channel)
    await db_session.commit()
    await db_session.refresh(channel)
    
    # Add creator as admin member
    channel_member = ChannelMember(
        user_id=test_user.id,
        channel_id=channel.id,
        role="admin"
    )
    db_session.add(channel_member)
    await db_session.commit()
    
    return channel


class TestChannelService:
    """Test channel service operations."""
    
    async def test_create_channel(
        self, 
        channel_service: ChannelService, 
        test_workspace: Workspace, 
        test_user: User
    ):
        """Test channel creation."""
        channel_data = ChannelCreate(
            name="new-channel",
            description="A new channel",
            type="public"
        )
        
        result = await channel_service.create_channel(
            test_workspace.id, channel_data, test_user.id
        )
        
        assert result.name == "new-channel"
        assert result.description == "A new channel"
        assert result.type == "public"
        assert result.workspace_id == test_workspace.id
        assert result.created_by == test_user.id
        assert result.user_role == "admin"
    
    async def test_create_private_channel(
        self, 
        channel_service: ChannelService, 
        test_workspace: Workspace, 
        test_user: User
    ):
        """Test private channel creation."""
        channel_data = ChannelCreate(
            name="private-channel",
            description="A private channel",
            type="private"
        )
        
        result = await channel_service.create_channel(
            test_workspace.id, channel_data, test_user.id
        )
        
        assert result.type == "private"
    
    async def test_get_channel(
        self, 
        channel_service: ChannelService, 
        test_channel: Channel, 
        test_user: User
    ):
        """Test getting channel by ID."""
        result = await channel_service.get_channel(test_channel.id, test_user.id)
        
        assert result.id == test_channel.id
        assert result.name == test_channel.name
        assert result.user_role == "admin"
    
    async def test_get_workspace_channels(
        self, 
        channel_service: ChannelService, 
        test_workspace: Workspace, 
        test_channel: Channel, 
        test_user: User
    ):
        """Test getting workspace channels."""
        result = await channel_service.get_workspace_channels(
            test_workspace.id, test_user.id
        )
        
        assert len(result) >= 1
        assert any(c.id == test_channel.id for c in result)
    
    async def test_get_workspace_channels_filter_by_type(
        self, 
        channel_service: ChannelService, 
        test_workspace: Workspace, 
        test_channel: Channel, 
        private_channel: Channel, 
        test_user: User
    ):
        """Test filtering channels by type."""
        # Get only public channels
        public_channels = await channel_service.get_workspace_channels(
            test_workspace.id, test_user.id, channel_type="public"
        )
        
        # Get only private channels
        private_channels = await channel_service.get_workspace_channels(
            test_workspace.id, test_user.id, channel_type="private"
        )
        
        assert any(c.id == test_channel.id for c in public_channels)
        assert any(c.id == private_channel.id for c in private_channels)
        assert not any(c.id == private_channel.id for c in public_channels)
        assert not any(c.id == test_channel.id for c in private_channels)
    
    async def test_update_channel(
        self, 
        channel_service: ChannelService, 
        test_channel: Channel, 
        test_user: User
    ):
        """Test channel update."""
        update_data = ChannelUpdate(
            name="updated-channel",
            description="Updated description"
        )
        
        result = await channel_service.update_channel(
            test_channel.id, update_data, test_user.id
        )
        
        assert result.name == "updated-channel"
        assert result.description == "Updated description"
    
    async def test_join_public_channel(
        self, 
        channel_service: ChannelService, 
        test_channel: Channel, 
        another_user: User,
        db_session: AsyncSession,
        test_workspace: Workspace
    ):
        """Test joining a public channel."""
        # Add another user to workspace
        user_workspace = UserWorkspace(
            user_id=another_user.id,
            workspace_id=test_workspace.id,
            role="member"
        )
        db_session.add(user_workspace)
        await db_session.commit()
        
        result = await channel_service.join_channel(test_channel.id, another_user.id)
        
        assert result.id == test_channel.id
        assert result.user_role == "member"
    
    async def test_cannot_join_private_channel(
        self, 
        channel_service: ChannelService, 
        private_channel: Channel, 
        another_user: User,
        db_session: AsyncSession,
        test_workspace: Workspace
    ):
        """Test that users cannot join private channels without invitation."""
        # Add another user to workspace
        user_workspace = UserWorkspace(
            user_id=another_user.id,
            workspace_id=test_workspace.id,
            role="member"
        )
        db_session.add(user_workspace)
        await db_session.commit()
        
        with pytest.raises(Exception):  # Should raise AuthorizationError
            await channel_service.join_channel(private_channel.id, another_user.id)
    
    async def test_invite_users_to_channel(
        self, 
        channel_service: ChannelService, 
        test_channel: Channel, 
        another_user: User,
        test_user: User,
        db_session: AsyncSession,
        test_workspace: Workspace
    ):
        """Test inviting users to channel."""
        # Add another user to workspace
        user_workspace = UserWorkspace(
            user_id=another_user.id,
            workspace_id=test_workspace.id,
            role="member"
        )
        db_session.add(user_workspace)
        await db_session.commit()
        
        results = await channel_service.invite_users_to_channel(
            test_channel.id, [another_user.id], test_user.id
        )
        
        assert len(results) == 1
        assert "Successfully invited" in results[0]
    
    async def test_leave_channel(
        self, 
        channel_service: ChannelService, 
        test_channel: Channel, 
        another_user: User,
        db_session: AsyncSession
    ):
        """Test leaving a channel."""
        # First add user to channel
        channel_member = ChannelMember(
            user_id=another_user.id,
            channel_id=test_channel.id,
            role="member"
        )
        db_session.add(channel_member)
        await db_session.commit()
        
        result = await channel_service.leave_channel(test_channel.id, another_user.id)
        
        assert result is True
    
    async def test_get_channel_members(
        self, 
        channel_service: ChannelService, 
        test_channel: Channel, 
        test_user: User
    ):
        """Test getting channel members."""
        result = await channel_service.get_channel_members(
            test_channel.id, test_user.id
        )
        
        assert result.total >= 1
        assert len(result.members) >= 1
        assert any(m.user_id == test_user.id for m in result.members)


class TestChannelAPI:
    """Test channel API endpoints."""
    
    async def test_create_channel_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_workspace: Workspace
    ):
        """Test POST /channels endpoint."""
        channel_data = {
            "name": "api-test-channel",
            "description": "Created via API",
            "type": "public"
        }
        
        response = await client.post(
            f"/api/v1/channels?workspace_id={test_workspace.id}",
            json=channel_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "api-test-channel"
        assert data["description"] == "Created via API"
        assert data["type"] == "public"
    
    async def test_get_workspace_channels_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_workspace: Workspace, 
        test_channel: Channel
    ):
        """Test GET /channels endpoint."""
        response = await client.get(
            f"/api/v1/channels?workspace_id={test_workspace.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(c["id"] == str(test_channel.id) for c in data)
    
    async def test_get_channel_by_id_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_channel: Channel
    ):
        """Test GET /channels/{channel_id} endpoint."""
        response = await client.get(
            f"/api/v1/channels/{test_channel.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_channel.id)
        assert data["name"] == test_channel.name
    
    async def test_update_channel_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_channel: Channel
    ):
        """Test PUT /channels/{channel_id} endpoint."""
        update_data = {
            "name": "updated-api-channel",
            "description": "Updated via API"
        }
        
        response = await client.put(
            f"/api/v1/channels/{test_channel.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated-api-channel"
        assert data["description"] == "Updated via API"
    
    async def test_join_channel_endpoint(
        self, 
        client: AsyncClient, 
        another_auth_headers: dict, 
        test_channel: Channel,
        db_session: AsyncSession,
        test_workspace: Workspace,
        another_user: User
    ):
        """Test POST /channels/{channel_id}/join endpoint."""
        # Add another user to workspace first
        user_workspace = UserWorkspace(
            user_id=another_user.id,
            workspace_id=test_workspace.id,
            role="member"
        )
        db_session.add(user_workspace)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/channels/{test_channel.id}/join",
            headers=another_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_channel.id)
    
    async def test_get_channel_members_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_channel: Channel
    ):
        """Test GET /channels/{channel_id}/members endpoint."""
        response = await client.get(
            f"/api/v1/channels/{test_channel.id}/members",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["members"]) >= 1
    
    async def test_invite_users_to_channel_endpoint(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_channel: Channel,
        another_user: User,
        db_session: AsyncSession,
        test_workspace: Workspace
    ):
        """Test POST /channels/{channel_id}/invite endpoint."""
        # Add another user to workspace first
        user_workspace = UserWorkspace(
            user_id=another_user.id,
            workspace_id=test_workspace.id,
            role="member"
        )
        db_session.add(user_workspace)
        await db_session.commit()
        
        invite_data = {
            "user_ids": [str(another_user.id)]
        }
        
        response = await client.post(
            f"/api/v1/channels/{test_channel.id}/invite",
            json=invite_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
    
    async def test_private_channel_access_control(
        self, 
        client: AsyncClient, 
        another_auth_headers: dict, 
        private_channel: Channel,
        db_session: AsyncSession,
        test_workspace: Workspace,
        another_user: User
    ):
        """Test that non-members can't access private channels."""
        # Add another user to workspace but not to private channel
        user_workspace = UserWorkspace(
            user_id=another_user.id,
            workspace_id=test_workspace.id,
            role="member"
        )
        db_session.add(user_workspace)
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/channels/{private_channel.id}",
            headers=another_auth_headers
        )
        
        assert response.status_code == 403