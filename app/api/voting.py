from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from typing import Optional, Literal

from app.models.character import Character
from app.models.film import Film
from app.models.starship import Starship
from app.schemas.vote import VoteSchema
from app.services.database import get_db
from app.utils.error_handling import NotFoundError, ValidationError

router = APIRouter(prefix="/vote", tags=["voting"])

EntityType = Literal["character", "film", "starship"]

ENTITY_MAP = {"character": Character, "film": Film, "starship": Starship}


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Vote for entity",
    description="Record a vote for a Star Wars character, film, or starship",
)
async def vote_for_entity(vote: VoteSchema, db: AsyncSession = Depends(get_db)):
    """
    Record a vote for a Star Wars entity (character, film, or starship).

    Parameters:
    - **entity_type**: Type of entity to vote for ('character', 'film', or 'starship')
    - **entity_id**: ID of the entity to vote for

    Returns:
    - Success message confirming the vote was recorded

    Example request body:
    ```json
    {
        "entity_type": "character",
        "entity_id": 1
    }
    ```
    """
    entity_type = vote.entity_type
    entity_id = vote.entity_id

    if entity_type not in ENTITY_MAP:
        raise ValidationError(f"Invalid entity type: {entity_type}")

    entity_model = ENTITY_MAP[entity_type]

    try:
        # Check if entity exists
        result = await db.execute(
            select(entity_model).filter(entity_model.id == entity_id)
        )
        entity = result.scalar_one_or_none()

        if not entity:
            raise NotFoundError(
                f"{entity_type.capitalize()} with ID {entity_id} not found"
            )

        # Update vote count
        stmt = (
            update(entity_model)
            .where(entity_model.id == entity_id)
            .values(votes=entity_model.votes + 1)
        )
        await db.execute(stmt)
        await db.commit()

        return {"message": f"Vote for {entity_type} {entity_id} recorded successfully"}

    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record vote: {str(e)}",
        )


@router.get(
    "/top",
    status_code=status.HTTP_200_OK,
    summary="Get top voted entities",
    description="Get the most popular Star Wars entities based on votes",
)
async def get_top_entities(
    entity_type: Optional[EntityType] = Query(
        None, description="Filter by entity type"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top voted Star Wars entities.

    Parameters:
    - **entity_type**: Optional filter by entity type ('character', 'film', or 'starship')
    - **limit**: Number of top results to return (default: 10, max: 100)

    Returns:
    - List of top entities grouped by entity type
    """
    results = {}

    try:
        if entity_type:
            # Filter by entity type
            if entity_type not in ENTITY_MAP:
                raise ValidationError(f"Invalid entity type: {entity_type}")

            entity_model = ENTITY_MAP[entity_type]
            query = select(entity_model).order_by(desc(entity_model.votes)).limit(limit)
            result = await db.execute(query)
            entities = result.scalars().all()

            results[entity_type] = [
                {
                    "id": entity.id,
                    "name": entity.name if hasattr(entity, "name") else entity.title,
                    "votes": entity.votes,
                }
                for entity in entities
            ]
        else:
            # Get top entities for all types
            for entity_name, entity_model in ENTITY_MAP.items():
                query = (
                    select(entity_model).order_by(desc(entity_model.votes)).limit(limit)
                )
                result = await db.execute(query)
                entities = result.scalars().all()

                results[entity_name] = [
                    {
                        "id": entity.id,
                        "name": (
                            entity.name if hasattr(entity, "name") else entity.title
                        ),
                        "votes": entity.votes,
                    }
                    for entity in entities
                ]

        return results

    except ValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top entities: {str(e)}",
        )
