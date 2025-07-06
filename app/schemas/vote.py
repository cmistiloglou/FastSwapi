from typing import Literal
from pydantic import BaseModel, Field


class VoteSchema(BaseModel):
    """Schema for voting on Star Wars entities"""

    entity_type: Literal["character", "film", "starship"] = Field(
        ..., description="Type of entity to vote for", example="character"
    )
    entity_id: int = Field(..., description="ID of the entity to vote for", example=1)

    class Config:
        json_schema_extra = {"example": {"entity_type": "character", "entity_id": 1}}
