import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_list_starships(async_client, db_with_starship):
    """Test listing all starships"""
    response = await async_client.get("/api/v1/starships/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "X-wing"
    assert "pilots" in data[0]  # Verify eager loading works


@pytest.mark.asyncio
async def test_get_starship(async_client, db_with_starship):
    """Test getting a specific starship"""
    response = await async_client.get("/api/v1/starships/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "X-wing"
    assert data["model"] == "T-65 X-wing"


@pytest.mark.asyncio
async def test_get_starship_not_found(async_client):
    """Test getting a non-existent starship"""
    response = await async_client.get("/api/v1/starships/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_starships(async_client, db_with_starship):
    """Test searching for starships"""
    # Test exact match
    response = await async_client.get("/api/v1/starships/search/?name=X-wing")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "X-wing"

    # Test case insensitive search
    response = await async_client.get("/api/v1/starships/search/?name=x-wing")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Test no results
    response = await async_client.get("/api/v1/starships/search/?name=NonExistent")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_fetch_starships(async_client, db_session, mock_swapi_service):
    """Test fetching starships from SWAPI"""
    # Setup mock return data with distinct swapi_ids
    mock_starships = [
        {
            "name": "X-wing",
            "model": "T-65 X-wing",
            "manufacturer": "Incom Corporation",
            "cost_in_credits": "149999",
            "length": "12.5",
            "max_atmosphering_speed": "1050",
            "crew": "1",
            "passengers": "0",
            "cargo_capacity": "110",
            "consumables": "1 week",
            "hyperdrive_rating": "1.0",
            "MGLT": "100",
            "starship_class": "Starfighter",
            "url": "https://swapi.info/api/starships/12/",
            "pilots": [],
        },
        {
            "name": "TIE Fighter",
            "model": "Twin Ion Engine/LN Starfighter",
            "manufacturer": "Sienar Fleet Systems",
            "cost_in_credits": "unknown",
            "length": "6.4",
            "max_atmosphering_speed": "1200",
            "crew": "1",
            "passengers": "0",
            "cargo_capacity": "65",
            "consumables": "2 days",
            "hyperdrive_rating": "unknown",
            "MGLT": "100",
            "starship_class": "Starfighter",
            "url": "https://swapi.info/api/starships/13/",
            "pilots": [],
        },
    ]

    # Configure mock
    mock_swapi_service.get_starships.return_value = mock_starships

    # Test the endpoint with a better mocking approach
    with patch("app.api.starships.SwapiService", return_value=mock_swapi_service):
        # Mock the extract_swapi_id function to return different IDs based on URL
        with patch("app.api.starships.extract_swapi_id", side_effect=[12, 13]):
            response = await async_client.post("/api/v1/starships/fetch")
            assert response.status_code == 201
            data = response.json()
            assert "created" in data


@pytest.mark.asyncio
async def test_database_error_in_list_starships(async_client):
    """Test handling database errors in list starships endpoint"""
    # Mock a database error
    with patch("app.api.starships.select", side_effect=Exception("Database error")):
        response = await async_client.get("/api/v1/starships/")
        assert response.status_code == 500
        assert "Failed to retrieve starships" in response.json()["detail"]
