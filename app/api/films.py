from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
import logging

from app.models.film import Film
from app.schemas.film import FilmSchema
from app.services.database import get_db
from app.utils.swapi_helpers import extract_swapi_id
from app.services.swapi import SwapiService
from app.utils.error_handling import (
    handle_external_api_error,
    DatabaseError,
    NotFoundError,
)

router = APIRouter(prefix="/films", tags=["films"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=List[FilmSchema],
    summary="List films",
    description="Get all Star Wars films",
)
async def list_films(db: AsyncSession = Depends(get_db)):
    """
    Get a list of all Star Wars films in the database.

    Returns:
    - List of films
    """
    try:
        query = select(Film).order_by(Film.title).options(selectinload(Film.characters))
        result = await db.execute(query)
        films = result.scalars().all()
        return films
    except Exception as e:
        logger.error(f"Error retrieving films: {str(e)}")
        raise DatabaseError(detail="Failed to retrieve films", internal_error=e)


@router.get(
    "/{film_id}",
    response_model=FilmSchema,
    summary="Get film",
    description="Get details of a specific Star Wars film",
)
async def get_film(film_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get detailed information about a specific Star Wars film.

    Parameters:
    - **film_id**: The ID of the film to retrieve

    Returns:
    - Film details including relationships to characters
    """
    try:
        result = await db.execute(
            select(Film)
            .filter(Film.id == film_id)
            .options(selectinload(Film.characters))
        )
        film = result.scalar_one_or_none()

        if not film:
            raise NotFoundError(f"Film with ID {film_id} not found")

        return film
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Error retrieving film: {str(e)}")
        raise DatabaseError(detail="Failed to retrieve film", internal_error=e)


@router.get(
    "/search/",
    response_model=List[FilmSchema],
    summary="Search films",
    description="Search for Star Wars films by title (case insensitive)",
)
async def search_films(
    title: str = Query(..., min_length=1, description="Title to search for"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for Star Wars films by title.

    Parameters:
    - **title**: The title or partial title to search for (case insensitive)

    Returns:
    - List of films matching the search criteria
    """
    try:
        query = (
            select(Film)
            .filter(Film.title.ilike(f"%{title}%"))
            .order_by(Film.title)
            .options(selectinload(Film.characters))
        )

        result = await db.execute(query)
        films = result.scalars().all()

        return films
    except Exception as e:
        logger.error(f"Error searching films: {str(e)}")
        raise DatabaseError(detail="Failed to search films", internal_error=e)


@router.post(
    "/fetch",
    status_code=status.HTTP_201_CREATED,
    summary="Fetch films from SWAPI",
    description="Fetch films from the Star Wars API and store them in the database",
)
async def fetch_films(db: AsyncSession = Depends(get_db)):
    """
    Fetch films from the Star Wars API (SWAPI) and store them in the database.

    This endpoint will:
    1. Connect to SWAPI
    2. Download all film data
    3. Save new films to the database (skips existing films)

    Returns:
    - Success message when complete
    """
    swapi_service = SwapiService()

    try:
        # Fetch films from SWAPI
        films = await handle_external_api_error(lambda: swapi_service.get_films())

        # Track statistics
        created_count = 0
        skipped_count = 0

        # Store each film in the database
        for film_data in films:
            film_data["swapi_id"] = extract_swapi_id(film_data["url"])

            # Check if film already exists
            existing = await db.execute(
                select(Film).filter(Film.swapi_id == film_data["swapi_id"])
            )
            if existing.scalar_one_or_none():
                skipped_count += 1
                continue

            # Create new film
            film = Film(
                title=film_data["title"],
                episode_id=film_data["episode_id"],
                opening_crawl=film_data["opening_crawl"],
                director=film_data["director"],
                producer=film_data["producer"],
                release_date=film_data["release_date"],
                url=film_data["url"],
                swapi_id=film_data["swapi_id"],
            )

            db.add(film)
            created_count += 1

        await db.commit()
        return {
            "message": "Films fetched and stored successfully",
            "created": created_count,
            "skipped": skipped_count,
            "total": created_count + skipped_count,
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error fetching films: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch and store films: {str(e)}",
        )
    finally:
        await swapi_service.close_session()
