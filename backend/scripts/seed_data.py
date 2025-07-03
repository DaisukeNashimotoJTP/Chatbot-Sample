"""
Seed script to create initial data for development and testing.
"""
import asyncio
from uuid import uuid4

from sqlalchemy import text
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.workspace import Workspace, UserWorkspace
from app.models.channel import Channel, ChannelMember
from app.models.message import Message


async def create_test_users():
    """Create test users for development."""
    async with AsyncSessionLocal() as session:
        # Check if users already exist
        existing_users = await session.execute(
            text("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL")
        )
        count = existing_users.scalar()
        
        if count > 0:
            print(f"Found {count} existing users. Skipping user creation.")
            return
        
        # Create test users
        test_users = [
            {
                "username": "admin",
                "email": "admin@chatservice.com",
                "password": "Admin123123",
                "display_name": "Admin User",
                "status": "active",
                "email_verified": True,
            },
            {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securePassword123",
                "display_name": "John Doe",
                "status": "active",
                "email_verified": True,
            },
            {
                "username": "janedoe",
                "email": "jane@example.com",
                "password": "securePassword123",
                "display_name": "Jane Doe",
                "status": "active",
                "email_verified": True,
            },
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "securePassword123",
                "display_name": "Test User",
                "status": "active",
                "email_verified": False,
            },
        ]
        
        for user_data in test_users:
            password = user_data.pop("password")
            password_hash = get_password_hash(password)
            
            user = User(
                id=uuid4(),
                password_hash=password_hash,
                **user_data
            )
            session.add(user)
        
        await session.commit()
        print(f"Created {len(test_users)} test users.")


async def create_test_workspaces():
    """Create test workspaces and channels."""
    async with AsyncSessionLocal() as session:
        # Check if workspaces already exist
        existing_workspaces = await session.execute(
            text("SELECT COUNT(*) FROM workspaces WHERE deleted_at IS NULL")
        )
        count = existing_workspaces.scalar()
        
        if count > 1:  # Allow the one existing workspace
            print(f"Found {count} existing workspaces. Skipping workspace creation.")
            return
            
        # Get admin user
        admin_result = await session.execute(
            text("SELECT id FROM users WHERE email = 'admin@chatservice.com' AND deleted_at IS NULL")
        )
        admin_id = admin_result.scalar()
        
        if not admin_id:
            print("Admin user not found. Skipping workspace creation.")
            return
            
        # Create additional test workspace
        test_workspace = Workspace(
            id=uuid4(),
            name="Development Team",
            slug="development-team",
            description="Workspace for development discussions",
            owner_id=admin_id,
            is_public=True,
            invite_code="dev2025"
        )
        session.add(test_workspace)
        await session.commit()
        await session.refresh(test_workspace)
        
        # Add admin as owner member
        user_workspace = UserWorkspace(
            user_id=admin_id,
            workspace_id=test_workspace.id,
            role="owner"
        )
        session.add(user_workspace)
        
        # Create test channels
        channels_data = [
            {
                "name": "general",
                "description": "General discussion for the team",
                "type": "public"
            },
            {
                "name": "development",
                "description": "Development discussions and updates",
                "type": "public"
            },
            {
                "name": "random",
                "description": "Random conversations and fun stuff",
                "type": "public"
            },
            {
                "name": "private-team",
                "description": "Private channel for core team",
                "type": "private"
            }
        ]
        
        created_channels = []
        for channel_data in channels_data:
            channel = Channel(
                id=uuid4(),
                workspace_id=test_workspace.id,
                name=channel_data["name"],
                description=channel_data["description"],
                type=channel_data["type"],
                created_by=admin_id
            )
            session.add(channel)
            created_channels.append(channel)
        
        await session.commit()
        
        # Add admin as admin member to all channels
        for channel in created_channels:
            await session.refresh(channel)
            channel_member = ChannelMember(
                user_id=admin_id,
                channel_id=channel.id,
                role="admin"
            )
            session.add(channel_member)
            
        await session.commit()
        print(f"Created test workspace with {len(created_channels)} channels.")


async def create_test_messages():
    """Create test messages in channels."""
    async with AsyncSessionLocal() as session:
        # Check if messages already exist
        existing_messages = await session.execute(
            text("SELECT COUNT(*) FROM messages WHERE deleted_at IS NULL")
        )
        count = existing_messages.scalar()
        
        if count > 2:  # Allow the existing messages
            print(f"Found {count} existing messages. Skipping message creation.")
            return
            
        # Get admin user and a channel
        admin_result = await session.execute(
            text("SELECT id FROM users WHERE email = 'admin@chatservice.com' AND deleted_at IS NULL")
        )
        admin_id = admin_result.scalar()
        
        channel_result = await session.execute(
            text("SELECT id FROM channels WHERE name = 'general' AND deleted_at IS NULL LIMIT 1")
        )
        channel_id = channel_result.scalar()
        
        if not admin_id or not channel_id:
            print("Admin user or general channel not found. Skipping message creation.")
            return
            
        # Create test messages
        test_messages = [
            "Welcome to the team chat! 👋",
            "Feel free to introduce yourselves here.",
            "We use this channel for general discussions and announcements.",
            "Don't forget to check out the #development channel for tech talks! 🚀",
            "Have a great day everyone! ☀️"
        ]
        
        for content in test_messages:
            message = Message(
                id=uuid4(),
                channel_id=channel_id,
                user_id=admin_id,
                content=content,
                message_type="text"
            )
            session.add(message)
            
        await session.commit()
        print(f"Created {len(test_messages)} test messages.")


async def main():
    """Main function to run all seed operations."""
    print("Starting database seeding...")
    
    # Initialize database
    await init_db()
    print("Database initialized.")
    
    # Create test data
    await create_test_users()
    await create_test_workspaces()
    await create_test_messages()
    
    print("Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())