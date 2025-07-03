"""
Seed script to create initial data for development and testing.
"""
import asyncio
from uuid import uuid4

from sqlalchemy import text
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User


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


async def main():
    """Main function to run all seed operations."""
    print("Starting database seeding...")
    
    # Initialize database
    await init_db()
    print("Database initialized.")
    
    # Create test data
    await create_test_users()
    
    print("Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())