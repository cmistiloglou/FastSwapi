from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.services.database import Base

# Association tables for many-to-many relationships
character_film = Table(
    "character_film",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id")),
    Column("film_id", Integer, ForeignKey("films.id")),
)

character_starship = Table(
    "character_starship",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id")),
    Column("starship_id", Integer, ForeignKey("starships.id")),
)


class Character(Base):
    """SQLAlchemy model for Star Wars characters"""

    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    height = Column(String)
    mass = Column(String)
    hair_color = Column(String)
    skin_color = Column(String)
    eye_color = Column(String)
    birth_year = Column(String)
    gender = Column(String)
    homeworld = Column(String)
    swapi_id = Column(Integer, unique=True, index=True)
    url = Column(String, unique=True)
    votes = Column(Integer, default=0)

    # Relationships
    films = relationship("Film", secondary=character_film, back_populates="characters")
    starships = relationship(
        "Starship", secondary=character_starship, back_populates="pilots"
    )
