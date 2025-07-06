from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.character import Character
from app.schemas.character import CharacterSchema
from app.services.database import get_db
from app.services.swapi import SwapiService
from app.utils.swapi_helpers import extract_swapi_id
from app.utils.error_handling import (
    handle_external_api_error,
    DatabaseError,
    NotFoundError,
)

router = APIRouter(prefix="/characters", tags=["characters"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=List[CharacterSchema],
    summary="List characters",
    description="Get all Star Wars characters",
)
async def list_characters(db: AsyncSession = Depends(get_db)):
    """
    Get a list of all Star Wars characters in the database.

    Returns:
    - List of characters
    """
    try:
        # Get all characters ordered by name
        query = select(Character).order_by(Character.name)
        result = await db.execute(query)
        characters = result.scalars().all()

        return characters
    except Exception as e:
        logger.error(f"Error retrieving characters: {str(e)}")
        raise DatabaseError(detail="Failed to retrieve characters", internal_error=e)


@router.get(
    "/{character_id}",
    response_model=CharacterSchema,
    summary="Get character",
    description="Get details of a specific Star Wars character",
)
async def get_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get detailed information about a specific Star Wars character.

    Parameters:
    - **character_id**: The ID of the character to retrieve

    Returns:
    - Character details including relationships to films and starships
    """
    try:
        result = await db.execute(
            select(Character).filter(Character.id == character_id)
        )
        character = result.scalar_one_or_none()

        if not character:
            raise NotFoundError(f"Character with ID {character_id} not found")

        return character
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Error retrieving character: {str(e)}")
        raise DatabaseError(detail="Failed to retrieve character", internal_error=e)


@router.get(
    "/search/",
    response_model=List[CharacterSchema],
    summary="Search characters",
    description="Search for Star Wars characters by name (case insensitive)",
)
async def search_characters(
    name: str = Query(..., min_length=1, description="Name to search for"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for Star Wars characters by name.

    Parameters:
    - **name**: The name or partial name to search for (case insensitive)

    Returns:
    - List of characters matching the search criteria
    """
    try:
        query = (
            select(Character)
            .filter(Character.name.ilike(f"%{name}%"))
            .order_by(Character.name)
        )

        result = await db.execute(query)
        characters = result.scalars().all()

        return characters
    except Exception as e:
        logger.error(f"Error searching characters: {str(e)}")
        raise DatabaseError(detail="Failed to search characters", internal_error=e)


@router.post(
    "/fetch",
    status_code=status.HTTP_201_CREATED,
    summary="Fetch characters from SWAPI",
    description="Fetch characters from the Star Wars API and store them in the database",
)
async def fetch_characters(db: AsyncSession = Depends(get_db)):
    """
    Fetch characters from the Star Wars API (SWAPI) and store them in the database.

    This endpoint will:
    1. Connect to SWAPI
    2. Download all character data
    3. Save new characters to the database (skips existing characters)

    Returns:
    - Success message when complete
    """
    swapi_service = SwapiService()

    try:
        # Fetch characters from SWAPI
        characters = await handle_external_api_error(
            lambda: swapi_service.get_characters()
        )

        # Track statistics
        created_count = 0
        skipped_count = 0

        # Store each character in the database
        for char_data in characters:
            char_data["swapi_id"] = extract_swapi_id(char_data["url"])

            # Check if character already exists
            existing = await db.execute(
                select(Character).filter(Character.swapi_id == char_data["swapi_id"])
            )
            if existing.scalar_one_or_none():
                skipped_count += 1
                continue

            # Create new character
            character = Character(
                name=char_data["name"],
                height=char_data["height"],
                mass=char_data["mass"],
                hair_color=char_data["hair_color"],
                skin_color=char_data["skin_color"],
                eye_color=char_data["eye_color"],
                birth_year=char_data["birth_year"],
                gender=char_data["gender"],
                homeworld=char_data["homeworld"],
                url=char_data["url"],
                swapi_id=char_data["swapi_id"],
            )

            db.add(character)
            created_count += 1

        await db.commit()
        return {
            "message": "Characters fetched and stored successfully",
            "created": created_count,
            "skipped": skipped_count,
            "total": created_count + skipped_count,
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error fetching characters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch and store characters: {str(e)}",
        )
    finally:
        await swapi_service.close_session()
