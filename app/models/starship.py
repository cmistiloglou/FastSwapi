from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.services.database import Base
from app.models.character import character_starship


class Starship(Base):
    """SQLAlchemy model for Star Wars starships"""

    __tablename__ = "starships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    model = Column(String)
    manufacturer = Column(String)
    cost_in_credits = Column(String)
    length = Column(String)
    max_atmosphering_speed = Column(String)
    crew = Column(String)
    passengers = Column(String)
    cargo_capacity = Column(String)
    consumables = Column(String)
    hyperdrive_rating = Column(String)
    MGLT = Column(String)
    starship_class = Column(String)
    swapi_id = Column(Integer, unique=True, index=True)
    url = Column(String, unique=True)
    votes = Column(Integer, default=0)

    # Relationships
    pilots = relationship(
        "Character", secondary=character_starship, back_populates="starships"
    )
