import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    """Test the root endpoint"""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to the FastSwapi API" in data["message"]
    assert "docs_url" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check(async_client):
    """Test the health check endpoint"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_error_handler(async_client):
    """Test the custom API error handler"""
    # Create an endpoint that raises a custom APIError
    with patch("app.main.app.router.routes", new=[]):
        from fastapi import APIRouter
        from app.utils.error_handling import APIError

        router = APIRouter()

        @router.get("/test-error")
        async def test_error():
            raise APIError(status_code=418, detail="I'm a teapot")

        # Add the router to the app
        from app.main import app

        app.include_router(router)

        # Test the endpoint
        response = await async_client.get("/test-error")
        assert response.status_code == 418
        assert response.json()["detail"] == "I'm a teapot"
