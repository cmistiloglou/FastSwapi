import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.services.database import Base, get_db
from app.models.character import Character
from app.models.film import Film
from app.models.starship import Starship

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for each test case"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    # Override database URL for testing
    with patch("app.services.database.DATABASE_URL", TEST_DATABASE_URL):
        engine = create_async_engine(TEST_DATABASE_URL, echo=False)

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        # Drop tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test"""
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session_maker = sessionmaker(
        autocommit=False, autoflush=False, bind=connection, class_=AsyncSession
    )

    async with session_maker() as session:
        yield session

    # Rollback transaction and close connection
    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def async_client(db_session):
    """Create an async test client that doesn't start a server"""

    # Override dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create client with direct ASGI transport
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_client(db_session):
    """Create a synchronous test client"""

    # Create a dependency override
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture
def sample_character_data() -> Dict[str, Any]:
    return {
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
        "votes": 0,
    }


@pytest.fixture
def sample_film_data() -> Dict[str, Any]:
    return {
        "title": "A New Hope",
        "episode_id": 4,
        "opening_crawl": "It is a period of civil war...",
        "director": "George Lucas",
        "producer": "Gary Kurtz, Rick McCallum",
        "release_date": "1977-05-25",
        "url": "https://swapi.info/api/films/1/",
        "swapi_id": 1,
        "votes": 0,
    }


@pytest.fixture
def sample_starship_data() -> Dict[str, Any]:
    return {
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
        "votes": 0,
    }


@pytest.fixture
async def db_with_character(db_session, sample_character_data):
    """Create a test database with a sample character"""
    character = Character(**sample_character_data)
    db_session.add(character)
    await db_session.commit()
    return db_session


@pytest.fixture
async def db_with_film(db_session, sample_film_data):
    """Create a test database with a sample film"""
    film = Film(**sample_film_data)
    db_session.add(film)
    await db_session.commit()
    return db_session


@pytest.fixture
async def db_with_starship(db_session, sample_starship_data):
    """Create a test database with a sample starship"""
    starship = Starship(**sample_starship_data)
    db_session.add(starship)
    await db_session.commit()
    return db_session


@pytest.fixture
def mock_swapi_service():
    """Mock the SWAPI service"""
    with patch("app.services.swapi.SwapiService") as mock:
        service = mock.return_value
        service.get_characters = AsyncMock(
            return_value=[
                {
                    "name": "Luke Skywalker",
                    "url": "https://swapi.info/api/people/1/",
                    "height": "172",
                    "mass": "77",
                    "hair_color": "blond",
                    "skin_color": "fair",
                    "eye_color": "blue",
                    "birth_year": "19BBY",
                    "gender": "male",
                    "homeworld": "https://swapi.info/api/planets/1/",
                    "films": ["https://swapi.info/api/films/1/"],
                    "starships": ["https://swapi.info/api/starships/12/"],
                }
            ]
        )
        service.get_films = AsyncMock(
            return_value=[
                {
                    "title": "A New Hope",
                    "episode_id": 4,
                    "opening_crawl": "Text...",
                    "director": "George Lucas",
                    "producer": "Gary Kurtz",
                    "release_date": "1977-05-25",
                    "url": "https://swapi.info/api/films/1/",
                    "characters": ["https://swapi.info/api/people/1/"],
                }
            ]
        )
        service.get_starships = AsyncMock(
            return_value=[
                {
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
                    "pilots": ["https://swapi.info/api/people/1/"],
                }
            ]
        )
        service.close_session = AsyncMock()
        service._get_resource = AsyncMock()
        service.get_all_resources = AsyncMock()
        yield service


# Override database connection for all tests
@pytest.fixture(autouse=True)
def override_db_settings():
    """Override database settings for testing"""
    with patch.dict(
        "os.environ",
        {
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
        },
    ):
        # Also directly patch the database module
        with patch("app.services.database.DATABASE_URL", TEST_DATABASE_URL):
            yield
