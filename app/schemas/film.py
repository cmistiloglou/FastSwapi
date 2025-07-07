from typing import List, Optional
from pydantic import BaseModel, Field


class FilmSchema(BaseModel):
    """Schema for Star Wars film data"""

    # Regular fields
    id: Optional[int] = Field(
        None, description="Database ID", json_schema_extra={"example": 1}
    )
    title: str = Field(
        ..., description="Film title", json_schema_extra={"example": "A New Hope"}
    )
    episode_id: int = Field(
        ..., description="Episode number", json_schema_extra={"example": 4}
    )
    opening_crawl: str = Field(
        ...,
        description="Opening crawl text",
        json_schema_extra={"example": "It is a period of civil war..."},
    )
    director: str = Field(
        ..., description="Film director", json_schema_extra={"example": "George Lucas"}
    )
    producer: str = Field(
        ...,
        description="Film producer",
        json_schema_extra={"example": "Gary Kurtz, Rick McCallum"},
    )
    release_date: str = Field(
        ..., description="Release date", json_schema_extra={"example": "1977-05-25"}
    )
    url: str = Field(
        ...,
        description="SWAPI URL",
        json_schema_extra={"example": "https://swapi.info/api/films/1/"},
    )
    swapi_id: int = Field(
        ..., description="ID in SWAPI", json_schema_extra={"example": 1}
    )
    votes: int = Field(
        0,
        description="Number of votes for this film",
        json_schema_extra={"example": 50},
    )

    # Optional relationship fields
    characters: Optional[List[int]] = Field(
        None,
        description="List of character IDs",
        json_schema_extra={"example": [1, 2, 3]},
    )

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "A New Hope",
                "episode_id": 4,
                "opening_crawl": "It is a period of civil war...",
                "director": "George Lucas",
                "producer": "Gary Kurtz, Rick McCallum",
                "release_date": "1977-05-25",
                "url": "https://swapi.info/api/films/1/",
                "swapi_id": 1,
                "votes": 50,
                "characters": [1, 2, 3],
            }
        }
