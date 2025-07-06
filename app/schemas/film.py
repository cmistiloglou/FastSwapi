from typing import List, Optional
from pydantic import BaseModel, Field


class FilmSchema(BaseModel):
    """Schema for Star Wars film data"""

    # Regular fields
    id: Optional[int] = Field(None, example=1, description="Database ID")
    title: str = Field(..., example="A New Hope", description="Film title")
    episode_id: int = Field(..., example=4, description="Episode number")
    opening_crawl: str = Field(
        ..., example="It is a period of civil war...", description="Opening crawl text"
    )
    director: str = Field(..., example="George Lucas", description="Film director")
    producer: str = Field(
        ..., example="Gary Kurtz, Rick McCallum", description="Film producer"
    )
    release_date: str = Field(..., example="1977-05-25", description="Release date")
    url: str = Field(
        ..., example="https://swapi.info/api/films/1/", description="SWAPI URL"
    )
    swapi_id: int = Field(..., example=1, description="ID in SWAPI")
    votes: int = Field(0, example=50, description="Number of votes for this film")

    # Optional relationship fields
    characters: Optional[List[int]] = Field(
        None, example=[1, 2, 3], description="List of character IDs"
    )

    class Config:
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
