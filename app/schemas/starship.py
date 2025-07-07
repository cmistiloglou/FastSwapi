from typing import List, Optional
from pydantic import BaseModel, Field


class StarshipSchema(BaseModel):
    """Schema for Star Wars starship data"""

    # Regular fields
    id: Optional[int] = Field(
        None, description="Database ID", json_schema_extra={"example": 1}
    )
    name: str = Field(
        ..., description="Starship name", json_schema_extra={"example": "X-wing"}
    )
    model: str = Field(
        ..., description="Starship model", json_schema_extra={"example": "T-65 X-wing"}
    )
    manufacturer: str = Field(
        ...,
        description="Manufacturer",
        json_schema_extra={"example": "Incom Corporation"},
    )
    cost_in_credits: str = Field(
        ..., description="Cost in credits", json_schema_extra={"example": "149999"}
    )
    length: str = Field(
        ..., description="Length in meters", json_schema_extra={"example": "12.5"}
    )
    max_atmosphering_speed: str = Field(
        ...,
        description="Maximum atmosphering speed",
        json_schema_extra={"example": "1050"},
    )
    crew: str = Field(..., description="Crew size", json_schema_extra={"example": "1"})
    passengers: str = Field(
        ..., description="Passenger capacity", json_schema_extra={"example": "0"}
    )
    cargo_capacity: str = Field(
        ..., description="Cargo capacity in kg", json_schema_extra={"example": "110"}
    )
    consumables: str = Field(
        ...,
        description="Consumable supplies duration",
        json_schema_extra={"example": "1 week"},
    )
    hyperdrive_rating: str = Field(
        ..., description="Hyperdrive rating", json_schema_extra={"example": "1.0"}
    )
    MGLT: str = Field(
        ..., description="Megalights per hour", json_schema_extra={"example": "100"}
    )
    starship_class: str = Field(
        ..., description="Starship class", json_schema_extra={"example": "Starfighter"}
    )
    url: str = Field(
        ...,
        description="SWAPI URL",
        json_schema_extra={"example": "https://swapi.info/api/starships/12/"},
    )
    swapi_id: int = Field(
        ..., description="ID in SWAPI", json_schema_extra={"example": 12}
    )
    votes: int = Field(
        0,
        description="Number of votes for this starship",
        json_schema_extra={"example": 30},
    )

    # Optional relationship fields
    pilots: Optional[List[int]] = Field(
        None, description="List of pilot IDs", json_schema_extra={"example": [1, 9]}
    )

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "X-wing",
                "model": "T-65 X-wing",
                "manufacturer": "Incom Corporation",
                "cost_in_credits": "149999",
                "length": "12.5",
                "max_atmosphering_speed": "1050",
                "crew": "1",
                "passengers": "0",
                "cargo_capacity": "110",
                "consumables": "1 week",
                "hyperdrive_rating": "1.0",
                "MGLT": "100",
                "starship_class": "Starfighter",
                "url": "https://swapi.info/api/starships/12/",
                "swapi_id": 12,
                "votes": 30,
                "pilots": [1, 9],
            }
        }
