from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.starship import Starship
from app.schemas.starship import StarshipSchema
from app.services.database import get_db
from app.utils.swapi_helpers import extract_swapi_id
from app.services.swapi import SwapiService
from app.utils.error_handling import (
    handle_external_api_error,
    DatabaseError,
    NotFoundError,
)

router = APIRouter(prefix="/starships", tags=["starships"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=List[StarshipSchema],
    summary="List starships",
    description="Get all Star Wars starships",
)
async def list_starships(db: AsyncSession = Depends(get_db)):
    """
    Get a list of all Star Wars starships in the database.

    Returns:
    - List of starships
    """
    try:
        # Get all starships ordered by name
        query = select(Starship).order_by(Starship.name)
        result = await db.execute(query)
        starships = result.scalars().all()

        return starships
    except Exception as e:
        logger.error(f"Error retrieving starships: {str(e)}")
        raise DatabaseError(detail="Failed to retrieve starships", internal_error=e)


@router.get(
    "/{starship_id}",
    response_model=StarshipSchema,
    summary="Get starship",
    description="Get details of a specific Star Wars starship",
)
async def get_starship(starship_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get detailed information about a specific Star Wars starship.

    Parameters:
    - **starship_id**: The ID of the starship to retrieve

    Returns:
    - Starship details including relationships to pilots
    """
    try:
        result = await db.execute(select(Starship).filter(Starship.id == starship_id))
        starship = result.scalar_one_or_none()

        if not starship:
            raise NotFoundError(f"Starship with ID {starship_id} not found")

        return starship
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Error retrieving starship: {str(e)}")
        raise DatabaseError(detail="Failed to retrieve starship", internal_error=e)


@router.get(
    "/search/",
    response_model=List[StarshipSchema],
    summary="Search starships",
    description="Search for Star Wars starships by name (case insensitive)",
)
async def search_starships(
    name: str = Query(..., min_length=1, description="Name to search for"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for Star Wars starships by name.

    Parameters:
    - **name**: The name or partial name to search for (case insensitive)

    Returns:
    - List of starships matching the search criteria
    """
    try:
        query = (
            select(Starship)
            .filter(Starship.name.ilike(f"%{name}%"))
            .order_by(Starship.name)
        )

        result = await db.execute(query)
        starships = result.scalars().all()

        return starships
    except Exception as e:
        logger.error(f"Error searching starships: {str(e)}")
        raise DatabaseError(detail="Failed to search starships", internal_error=e)


@router.post(
    "/fetch",
    status_code=status.HTTP_201_CREATED,
    summary="Fetch starships from SWAPI",
    description="Fetch starships from the Star Wars API and store them in the database",
)
async def fetch_starships(db: AsyncSession = Depends(get_db)):
    """
    Fetch starships from the Star Wars API (SWAPI) and store them in the database.

    This endpoint will:
    1. Connect to SWAPI
    2. Download all starship data
    3. Save new starships to the database (skips existing starships)

    Returns:
    - Success message when complete
    """
    swapi_service = SwapiService()

    try:
        # Fetch starships from SWAPI
        starships = await handle_external_api_error(
            lambda: swapi_service.get_starships()
        )

        # Track statistics
        created_count = 0
        skipped_count = 0

        # Store each starship in the database
        for starship_data in starships:
            starship_data["swapi_id"] = extract_swapi_id(starship_data["url"])
            
            # Check if starship already exists
            existing = await db.execute(
                select(Starship).filter(Starship.swapi_id == starship_data["swapi_id"])
            )
            if existing.scalar_one_or_none():
                skipped_count += 1
                continue

            # Create new starship
            starship = Starship(
                name=starship_data["name"],
                model=starship_data["model"],
                manufacturer=starship_data["manufacturer"],
                cost_in_credits=starship_data["cost_in_credits"],
                length=starship_data["length"],
                max_atmosphering_speed=starship_data["max_atmosphering_speed"],
                crew=starship_data["crew"],
                passengers=starship_data["passengers"],
                cargo_capacity=starship_data["cargo_capacity"],
                consumables=starship_data["consumables"],
                hyperdrive_rating=starship_data["hyperdrive_rating"],
                MGLT=starship_data["MGLT"],
                starship_class=starship_data["starship_class"],
                url=starship_data["url"],
                swapi_id=starship_data["swapi_id"],
            )

            db.add(starship)
            created_count += 1

        await db.commit()
        return {
            "message": "Starships fetched and stored successfully",
            "created": created_count,
            "skipped": skipped_count,
            "total": created_count + skipped_count,
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error fetching starships: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch and store starships: {str(e)}",
        )
    finally:
        await swapi_service.close_session()
