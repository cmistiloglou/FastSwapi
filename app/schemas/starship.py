from typing import List, Optional
from pydantic import BaseModel, Field


class StarshipSchema(BaseModel):
    """Schema for Star Wars starship data"""

    # Regular fields
    id: Optional[int] = Field(None, example=1, description="Database ID")
    name: str = Field(..., example="X-wing", description="Starship name")
    model: str = Field(..., example="T-65 X-wing", description="Starship model")
    manufacturer: str = Field(
        ..., example="Incom Corporation", description="Manufacturer"
    )
    cost_in_credits: str = Field(..., example="149999", description="Cost in credits")
    length: str = Field(..., example="12.5", description="Length in meters")
    max_atmosphering_speed: str = Field(
        ..., example="1050", description="Maximum atmosphering speed"
    )
    crew: str = Field(..., example="1", description="Crew size")
    passengers: str = Field(..., example="0", description="Passenger capacity")
    cargo_capacity: str = Field(..., example="110", description="Cargo capacity in kg")
    consumables: str = Field(
        ..., example="1 week", description="Consumable supplies duration"
    )
    hyperdrive_rating: str = Field(..., example="1.0", description="Hyperdrive rating")
    MGLT: str = Field(..., example="100", description="Megalights per hour")
    starship_class: str = Field(
        ..., example="Starfighter", description="Starship class"
    )
    url: str = Field(
        ..., example="https://swapi.info/api/starships/12/", description="SWAPI URL"
    )
    swapi_id: int = Field(..., example=12, description="ID in SWAPI")
    votes: int = Field(0, example=30, description="Number of votes for this starship")

    # Optional relationship fields
    pilots: Optional[List[int]] = Field(
        None, example=[1, 9], description="List of pilot IDs"
    )

    class Config:
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
