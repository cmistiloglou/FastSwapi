import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.characters import router as characters_router
from app.api.films import router as films_router
from app.api.starships import router as starships_router
from app.api.voting import router as voting_router
from app.utils.error_handling import APIError
from app.services.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (runs before the application starts)
    await init_db()
    logger.info("Database tables initialized")

    yield

    # Shutdown code (runs when the application is shutting down)
    logger.info("Application shutdown")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Star Wars API",
        version="1.0.0",
        description="""
        # Star Wars API
        
        This API allows you to interact with Star Wars data and vote for your favorites.
        
        ## Features
        
        - **Data Source**: Fetches data from the Star Wars API (SWAPI)
        - **Characters**: Access information about Star Wars characters
        - **Films**: Access information about Star Wars films
        - **Starships**: Access information about Star Wars starships
        - **Voting**: Vote for your favorite characters, films, and starships
        - **Search**: Search functionality for all entity types
        
        ## Getting Started
        
        1. First, use the `/fetch` endpoints to populate your database with Star Wars data
        2. Browse and search the data using the provided endpoints
        3. Vote for your favorite Star Wars entities
        """,
        routes=app.routes,
    )

    # Add servers
    openapi_schema["servers"] = [{"url": "/", "description": "Current server"}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Create FastAPI app with lifespan
app = FastAPI(
    title="Star Wars API",
    description="A Star Wars API built with FastAPI that allows fetching and voting on Star Wars characters, films, and starships",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API prefix
API_V1_STR = "/api/v1"

# Register routers
app.include_router(characters_router, prefix=API_V1_STR)
app.include_router(films_router, prefix=API_V1_STR)
app.include_router(starships_router, prefix=API_V1_STR)
app.include_router(voting_router, prefix=API_V1_STR)

# Custom OpenAPI schema
app.openapi = custom_openapi


# Exception handler for custom API errors
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get(
    "/", summary="API Root", description="Welcome endpoint with basic API information"
)
async def root():
    """
    Root endpoint that provides basic API information.

    Returns:
    - Message with API name, documentation URL and version
    """
    return {
        "message": "Welcome to the FastSwapi API",
        "docs_url": "/docs",
        "version": "1.0.0",
    }


@app.get(
    "/health", summary="Health Check", description="Endpoint to check API health status"
)
async def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
    - Status indicating the API is operational
    """
    return {"status": "healthy"}
