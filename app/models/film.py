from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.services.database import Base
from app.models.character import character_film


class Film(Base):
    """SQLAlchemy model for Star Wars films"""

    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    episode_id = Column(Integer)
    opening_crawl = Column(String)
    director = Column(String)
    producer = Column(String)
    release_date = Column(String)
    swapi_id = Column(Integer, unique=True, index=True)
    url = Column(String, unique=True)
    votes = Column(Integer, default=0)

    # Relationships
    characters = relationship(
        "Character", secondary=character_film, back_populates="films"
    )
