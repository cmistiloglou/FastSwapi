from typing import List, Optional
from pydantic import BaseModel, Field


class CharacterSchema(BaseModel):
    """Schema for Star Wars character data"""

    # Regular fields
    id: Optional[int] = Field(
        None, description="Database ID", json_schema_extra={"example": 1}
    )
    name: str = Field(
        ...,
        description="Character name",
        json_schema_extra={"example": "Luke Skywalker"},
    )
    height: str = Field(
        ..., description="Character height in cm", json_schema_extra={"example": "172"}
    )
    mass: str = Field(
        ..., description="Character mass in kg", json_schema_extra={"example": "77"}
    )
    hair_color: str = Field(
        ..., description="Hair color", json_schema_extra={"example": "blond"}
    )
    skin_color: str = Field(
        ..., description="Skin color", json_schema_extra={"example": "fair"}
    )
    eye_color: str = Field(
        ..., description="Eye color", json_schema_extra={"example": "blue"}
    )
    birth_year: str = Field(
        ...,
        description="Birth year in Star Wars universe",
        json_schema_extra={"example": "19BBY"},
    )
    gender: str = Field(
        ..., description="Character gender", json_schema_extra={"example": "male"}
    )
    homeworld: str = Field(
        ...,
        description="URL of homeworld",
        json_schema_extra={"example": "https://swapi.info/api/planets/1/"},
    )
    url: str = Field(
        ...,
        description="SWAPI URL",
        json_schema_extra={"example": "https://swapi.info/api/people/1/"},
    )
    swapi_id: int = Field(
        ..., description="ID in SWAPI", json_schema_extra={"example": 1}
    )
    votes: int = Field(
        0,
        description="Number of votes for this character",
        json_schema_extra={"example": 42},
    )

    # Optional relationship fields
    films: Optional[List[int]] = Field(
        None, description="List of film IDs", json_schema_extra={"example": [1, 2, 3]}
    )
    starships: Optional[List[int]] = Field(
        None,
        description="List of starship IDs",
        json_schema_extra={"example": [12, 22]},
    )

    class ConfigDict:
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
