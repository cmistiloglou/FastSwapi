import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character


@pytest.mark.asyncio
async def test_get_db(db_session):
    """Test basic database operations with the session"""
    # Insert a test record
    character = Character(
        name="Test Character",
        height="180",
        mass="80",
        hair_color="brown",
        skin_color="light",
        eye_color="blue",
        birth_year="20BBY",
        gender="male",
        homeworld="https://swapi.info/api/planets/1/",
        url="https://test.com/1/",
        swapi_id=999,
    )
    db_session.add(character)
    await db_session.commit()

    # Query the record
    result = await db_session.execute(select(Character).filter_by(swapi_id=999))
    character = result.scalar_one()
    assert character.name == "Test Character"


@pytest.mark.asyncio
async def test_init_db(test_engine):
    """Test that database tables are created properly"""
    # Check if tables exist by executing a simple query
    async with AsyncSession(test_engine) as session:
        # This will fail if the characters table doesn't exist
        result = await session.execute(text("SELECT 1 FROM characters LIMIT 1"))
        # It doesn't matter if we get results, just that the query succeeds
        assert result is not None
