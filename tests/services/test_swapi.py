import pytest
from unittest.mock import patch
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.film import Film


@pytest.mark.asyncio
async def test_list_films(async_client, db_with_film):
    """Test listing all films"""
    response = await async_client.get("/api/v1/films/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "A New Hope"


@pytest.mark.asyncio
async def test_get_film(async_client, db_with_film):
    """Test getting a specific film"""
    response = await async_client.get("/api/v1/films/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "A New Hope"
    assert data["episode_id"] == 4


@pytest.mark.asyncio
async def test_get_film_not_found(async_client):
    """Test getting a non-existent film"""
    response = await async_client.get("/api/v1/films/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_films(async_client, db_with_film):
    """Test searching for films"""
    # Test exact match
    response = await async_client.get("/api/v1/films/search/?title=New Hope")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "A New Hope"

    # Test case insensitive search
    response = await async_client.get("/api/v1/films/search/?title=new hope")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Test no results
    response = await async_client.get("/api/v1/films/search/?title=NonExistent")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_fetch_films(async_client, db_session, mock_swapi_service):
    """Test fetching films from SWAPI"""
    # Setup mock return data
    mock_films = [
        {
            "title": "A New Hope",
            "episode_id": 4,
            "opening_crawl": "Text...",
            "director": "George Lucas",
            "producer": "Gary Kurtz",
            "release_date": "1977-05-25",
            "url": "https://swapi.info/api/films/1/",
            "characters": ["https://swapi.info/api/people/1/"],
        }
    ]

    # Configure mock
    mock_swapi_service.get_films.return_value = mock_films

    # Test the endpoint
    with patch("app.api.films.SwapiService", return_value=mock_swapi_service):
        with patch("app.api.films.extract_swapi_id", return_value=1):
            response = await async_client.post("/api/v1/films/fetch")
            assert response.status_code == 201
            data = response.json()
            assert "created" in data
