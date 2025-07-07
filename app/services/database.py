from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection parameters from environment
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Build connection string
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create async engine for database operations
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

# Create session factory for async database sessions
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create base class for SQLAlchemy models
Base = declarative_base()


# Database session dependency for FastAPI
async def get_db():
    """Dependency for getting database session in FastAPI endpoints"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize database function - we'll call this during startup
async def init_db():
    """Create database tables if they don't exist"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
