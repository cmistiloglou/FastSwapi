import pytest
from sqlalchemy import select
from unittest.mock import patch

from app.models.film import Film
from app.models.starship import Starship
from app.models.character import Character


@pytest.mark.asyncio
async def test_vote_for_character(async_client, db_with_character):
    """Test voting for a character"""
    # Get initial vote count
    result = await db_with_character.execute(
        select(Character).filter(Character.id == 1)
    )
    character = result.scalar_one()
    initial_votes = character.votes

    # Submit vote
    response = await async_client.post(
        "/api/v1/vote/", json={"entity_type": "character", "entity_id": 1}
    )

    assert response.status_code == 200
    assert "recorded successfully" in response.json()["message"]

    # Verify vote was recorded
    await db_with_character.refresh(character)
    assert character.votes == initial_votes + 1


@pytest.mark.asyncio
async def test_vote_for_film(async_client, db_with_film):
    """Test voting for a film"""
    # Get initial vote count
    result = await db_with_film.execute(select(Film).filter(Film.id == 1))
    film = result.scalar_one()
    initial_votes = film.votes

    # Submit vote
    response = await async_client.post(
        "/api/v1/vote/", json={"entity_type": "film", "entity_id": 1}
    )

    assert response.status_code == 200
    assert "recorded successfully" in response.json()["message"]

    # Verify vote was recorded
    await db_with_film.refresh(film)
    assert film.votes == initial_votes + 1


@pytest.mark.asyncio
async def test_vote_for_nonexistent_entity(async_client):
    """Test voting for an entity that doesn't exist"""
    response = await async_client.post(
        "/api/v1/vote/", json={"entity_type": "character", "entity_id": 999}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_top_entities(async_client, db_session):
    """Test getting top voted entities"""
    # Create characters with different vote counts
    characters = [
        Character(
            name=f"Character {i}",
            swapi_id=i,
            votes=i * 10,
            height="180",
            mass="80",
            hair_color="brown",
            skin_color="fair",
            eye_color="blue",
            birth_year="19BBY",
            gender="male",
            homeworld="https://swapi.info/api/planets/1/",
            url=f"https://swapi.info/api/people/{i}/",
        )
        for i in range(1, 6)
    ]

    for char in characters:
        db_session.add(char)
    await db_session.commit()

    # Test getting top characters
    response = await async_client.get("/api/v1/vote/top?entity_type=character&limit=3")
    assert response.status_code == 200
    data = response.json()

    assert "character" in data
    assert len(data["character"]) == 3

    # Should be sorted by votes descending
    assert data["character"][0]["name"] == "Character 5"
    assert data["character"][0]["votes"] == 50
    assert data["character"][1]["name"] == "Character 4"
    assert data["character"][1]["votes"] == 40


@pytest.mark.asyncio
async def test_vote_for_starship(async_client, db_session, sample_starship_data):
    """Test voting for a starship"""
    # Create a starship
    starship = Starship(**sample_starship_data)
    db_session.add(starship)
    await db_session.commit()

    # Submit vote
    response = await async_client.post(
        "/api/v1/vote/", json={"entity_type": "starship", "entity_id": 1}
    )

    assert response.status_code == 200
    assert "recorded successfully" in response.json()["message"]

    # Verify vote was recorded
    await db_session.refresh(starship)
    assert starship.votes == 1


@pytest.mark.asyncio
async def test_vote_database_error(async_client, db_with_character):
    """Test database error handling during voting"""
    with patch("app.api.voting.select", side_effect=Exception("Database error")):
        response = await async_client.post(
            "/api/v1/vote/", json={"entity_type": "character", "entity_id": 1}
        )

        assert response.status_code == 500
        assert "Failed to record vote" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_top_entities_database_error(async_client):
    """Test database error handling in top entities endpoint"""
    with patch("app.api.voting.select", side_effect=Exception("Database error")):
        response = await async_client.get("/api/v1/vote/top?entity_type=character")
        assert response.status_code == 500
        assert "Failed to get top entities" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_top_entities_filtered_by_film(async_client, db_session):
    """Test getting top voted films"""
    # Create films with different vote counts
    films = [
        Film(
            title=f"Film {i}",
            episode_id=i,
            opening_crawl=f"Opening crawl {i}",
            director="Director",
            producer="Producer",
            release_date="2023-01-01",
            url=f"https://swapi.info/api/films/{i}/",
            swapi_id=i + 100,  # Use unique swapi_ids
            votes=i * 10,
        )
        for i in range(1, 4)
    ]

    for film in films:
        db_session.add(film)
    await db_session.commit()

    # Test getting top films
    response = await async_client.get("/api/v1/vote/top?entity_type=film&limit=2")
    assert response.status_code == 200
    data = response.json()

    assert "film" in data
    assert len(data["film"]) == 2

    # Check using "name" key instead of "title" (the voting API uses "name" for everything)
    assert data["film"][0]["votes"] == 30
    assert (
        data["film"][0]["name"] == "Film 3"
    )  # The API standardizes on "name" in responses
