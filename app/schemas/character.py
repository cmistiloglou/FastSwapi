from typing import List, Optional
from pydantic import BaseModel, Field


class CharacterSchema(BaseModel):
    """Schema for Star Wars character data"""

    # Regular fields
    id: Optional[int] = Field(None, example=1, description="Database ID")
    name: str = Field(..., example="Luke Skywalker", description="Character name")
    height: str = Field(..., example="172", description="Character height in cm")
    mass: str = Field(..., example="77", description="Character mass in kg")
    hair_color: str = Field(..., example="blond", description="Hair color")
    skin_color: str = Field(..., example="fair", description="Skin color")
    eye_color: str = Field(..., example="blue", description="Eye color")
    birth_year: str = Field(
        ..., example="19BBY", description="Birth year in Star Wars universe"
    )
    gender: str = Field(..., example="male", description="Character gender")
    homeworld: str = Field(
        ..., example="https://swapi.info/api/planets/1/", description="URL of homeworld"
    )
    url: str = Field(
        ..., example="https://swapi.info/api/people/1/", description="SWAPI URL"
    )
    swapi_id: int = Field(..., example=1, description="ID in SWAPI")
    votes: int = Field(0, example=42, description="Number of votes for this character")

    # Optional relationship fields
    films: Optional[List[int]] = Field(
        None, example=[1, 2, 3], description="List of film IDs"
    )
    starships: Optional[List[int]] = Field(
        None, example=[12, 22], description="List of starship IDs"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Luke Skywalker",
                "height": "172",
                "mass": "77",
                "hair_color": "blond",
                "skin_color": "fair",
                "eye_color": "blue",
                "birth_year": "19BBY",
                "gender": "male",
                "homeworld": "https://swapi.info/api/planets/1/",
                "url": "https://swapi.info/api/people/1/",
                "swapi_id": 1,
                "votes": 42,
                "films": [1, 2, 3],
                "starships": [12, 22],
            }
        }
