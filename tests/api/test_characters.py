import pytest
from unittest.mock import patch
from sqlalchemy import select
from app.models.character import Character


@pytest.mark.asyncio
async def test_list_characters(async_client, db_with_character):
    """Test listing all characters"""
    response = await async_client.get("/api/v1/characters/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Luke Skywalker"


@pytest.mark.asyncio
async def test_get_character(async_client, db_with_character):
    """Test getting a specific character"""
    response = await async_client.get("/api/v1/characters/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Luke Skywalker"
    assert data["height"] == "172"


@pytest.mark.asyncio
async def test_get_character_not_found(async_client):
    """Test getting a non-existent character"""
    response = await async_client.get("/api/v1/characters/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_characters(async_client, db_with_character):
    """Test searching for characters"""
    # Test exact match
    response = await async_client.get("/api/v1/characters/search/?name=Luke")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Luke Skywalker"

    # Test case insensitive search
    response = await async_client.get("/api/v1/characters/search/?name=luke")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Test no results
    response = await async_client.get("/api/v1/characters/search/?name=NonExistent")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_fetch_characters(async_client, db_session, mock_swapi_service):
    """Test fetching characters from SWAPI"""
    # Setup mock return data
    mock_characters = [
        {
            "name": "Luke Skywalker",
            "height": "172",
            "mass": "77",
            "hair_color": "blond",
            "skin_color": "fair",
            "eye_color": "blue",
            "birth_year": "19BBY",
            "gender": "male",
            "homeworld": "https://swapi.info/api/planets/1/",
            "url": "https://swapi.info/api/people/1/",
            "films": ["https://swapi.info/api/films/1/"],
            "starships": ["https://swapi.info/api/starships/12/"],
        }
    ]

    # Configure mock
    mock_swapi_service.get_characters.return_value = mock_characters

    # Test the endpoint
    with patch("app.api.characters.SwapiService", return_value=mock_swapi_service):
        response = await async_client.post("/api/v1/characters/fetch")
        assert response.status_code == 201
        data = response.json()
        assert "created" in data

        # Verify database was updated
        result = await db_session.execute(select(Character))
        characters = result.scalars().all()
        assert len(characters) >= 1
        assert any(c.name == "Luke Skywalker" for c in characters)


@pytest.mark.asyncio
async def test_database_error_in_list_characters(async_client):
    """Test handling database errors in list characters endpoint"""
    # Mock a database error
    with patch("app.api.characters.select", side_effect=Exception("Database error")):
        response = await async_client.get("/api/v1/characters/")
        assert response.status_code == 500
        assert "Failed to retrieve characters" in response.json()["detail"]


@pytest.mark.asyncio
async def test_external_api_error_in_fetch_characters(async_client, mock_swapi_service):
    """Test handling external API errors in fetch characters endpoint"""
    # Configure the mock to raise an error
    mock_swapi_service.get_characters.side_effect = Exception("API error")

    with patch("app.api.characters.SwapiService", return_value=mock_swapi_service):
        response = await async_client.post("/api/v1/characters/fetch")
        assert response.status_code == 500
        assert "Failed to fetch" in response.json()["detail"]


@pytest.mark.asyncio
async def test_character_empty_results(async_client):
    """Test empty results from character search"""
    response = await async_client.get(
        "/api/v1/characters/search/?name=ThisNameDoesNotExist"
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_with_special_characters(async_client, db_session):
    """Test searching with special characters"""
    # Add a character with special characters
    character = Character(
        name="C-3PO & R2-D2",
        height="167",
        mass="75",
        hair_color="none",
        skin_color="gold",
        eye_color="yellow",
        birth_year="112BBY",
        gender="n/a",
        homeworld="https://swapi.info/api/planets/1/",
        url="https://swapi.info/api/people/2/",
        swapi_id=2,
    )
    db_session.add(character)
    await db_session.commit()

    # Test search with special characters
    response = await async_client.get("/api/v1/characters/search/?name=C-3PO%20%26")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "C-3PO & R2-D2"
