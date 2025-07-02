"""
Test authentication functionality.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash


class TestUserRegistration:
    """Test user registration endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "display_name": "Test User",
            "password": "testpassword123"
        }
        
        response = await client.post("/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "Test User"
        assert "password" not in data
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, db_session: AsyncSession):
        """Test registration with duplicate email."""
        # Create existing user
        existing_user = User(
            username="existing",
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            display_name="Existing User"
        )
        db_session.add(existing_user)
        await db_session.commit()
        
        # Try to register with same email
        user_data = {
            "username": "newuser",
            "email": "test@example.com",
            "display_name": "New User",
            "password": "testpassword123"
        }
        
        response = await client.post("/v1/auth/register", json=user_data)
        
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, db_session: AsyncSession):
        """Test registration with duplicate username."""
        # Create existing user
        existing_user = User(
            username="testuser",
            email="existing@example.com",
            password_hash=get_password_hash("password123"),
            display_name="Existing User"
        )
        db_session.add(existing_user)
        await db_session.commit()
        
        # Try to register with same username
        user_data = {
            "username": "testuser",
            "email": "new@example.com",
            "display_name": "New User",
            "password": "testpassword123"
        }
        
        response = await client.post("/v1/auth/register", json=user_data)
        
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_register_invalid_password(self, client: AsyncClient):
        """Test registration with invalid password."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "display_name": "Test User",
            "password": "weak"
        }
        
        response = await client.post("/v1/auth/register", json=user_data)
        
        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoints."""
    
    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful login with valid credentials."""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("testpassword123"),
            display_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Login
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with invalid email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, db_session: AsyncSession):
        """Test login with invalid password."""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("testpassword123"),
            display_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Login with wrong password
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/v1/auth/login", json=login_data)
        
        assert response.status_code == 401


class TestTokenRefresh:
    """Test token refresh functionality."""
    
    @pytest.mark.asyncio
    async def test_refresh_valid_token(self, client: AsyncClient, db_session: AsyncSession):
        """Test token refresh with valid refresh token."""
        # Create and login user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("testpassword123"),
            display_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Login to get refresh token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        login_response = await client.post("/v1/auth/login", json=login_data)
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


class TestProtectedEndpoints:
    """Test protected endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting current user info."""
        # Create and login user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("testpassword123"),
            display_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Login
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        login_response = await client.post("/v1/auth/login", json=login_data)
        login_data = login_response.json()
        access_token = login_data["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test protected endpoint without authentication token."""
        response = await client.get("/v1/auth/me")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_invalid_token(self, client: AsyncClient):
        """Test protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/v1/auth/me", headers=headers)
        
        assert response.status_code == 401