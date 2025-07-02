"""
Test main application functionality.
"""
import pytest
from httpx import AsyncClient


class TestHealthCheck:
    """Test health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint returns correct response."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_health_check_structure(self, client: AsyncClient):
        """Test health check response structure."""
        response = await client.get("/health")
        data = response.json()
        
        # Check required fields
        required_fields = ["status", "service", "version"]
        for field in required_fields:
            assert field in data
        
        # Check field types
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["version"], str)