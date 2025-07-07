# FastSwapi

A RESTful API built with FastAPI that interacts with the Star Wars API (SWAPI) to provide information about Star Wars characters, films, and starships, and allows voting for your favorites.

## Features

- Fetch Star Wars data from SWAPI
- Store and retrieve characters, films, and starships
- Search functionality by name/title
- Voting system for favorite Star Wars entities
- Comprehensive API documentation with Swagger UI
- Error handling and validation
- Asynchronous HTTP requests with aiohttp
- Automated testing with pytest

## Technology Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy ORM with async support
- Docker & Docker Compose
- aiohttp for async HTTP requests
- Pytest for testing

## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository `git clone https://github.com/cmistiloglou/FastSwapi.git`

2. Change directory to FastSwapi and create `.env` in the root directory

3. Build the images `docker compose build`

4. Start the containers `docker compose up -d`

5. The API will be available at `http://localhost:8000`

6. API Documentation: `http://localhost:8000/docs`

## Populating the Database

Before you can use the API effectively, you need to populate the database with data from SWAPI. <br> You have three options:

### Option 1: Using cURL

```bash
# Fetch characters
curl -X POST http://localhost:8000/api/v1/characters/fetch

# Fetch films
curl -X POST http://localhost:8000/api/v1/films/fetch

## Fetch starships
curl -X POST http://localhost:8000/api/v1/starships/fetch
```

### Option 2: Using Swagger UI

Open your browser and go to `http://localhost:8000/docs`

Find each of the **"fetch"** endpoints in the documentation. <br>
Click on each endpoint, then click the **"Try it out"** button. <br>
Click **"Execute"** to run the request.

### Option 3: Using the API Client of Your Choice

You can use tools like Postman or Insomnia to make POST requests to:

```bash
http://localhost:8000/api/v1/films/fetch 
http://localhost:8000/api/v1/starships/fetch 
http://localhost:8000/api/v1/characters/fetch 
```

## Verifying Database Population

To verify the data was successfully imported:

```bash
# Check imported characters
curl http://localhost:8000/api/v1/characters/

# Check imported films
curl http://localhost:8000/api/v1/films/

# Check imported starships
curl http://localhost:8000/api/v1/starships/
```

Or use the GET endpoints in the Swagger UI.

## API Endpoints

### Characters

- `GET /api/v1/characters/` - List all characters
- `GET /api/v1/characters/{id}` - Get character by ID
- `GET /api/v1/characters/search/?name={query}` - Search characters by name
- `POST /api/v1/characters/fetch` - Fetch characters from SWAPI

### Films

- `GET /api/v1/films/` - List all films
- `GET /api/v1/films/{id}` - Get film by ID
- `GET /api/v1/films/search/?title={query}` - Search films by title
- `POST /api/v1/films/fetch` - Fetch films from SWAPI

### Starships

- `GET /api/v1/starships/` - List all starships
- `GET /api/v1/starships/{id}` - Get starship by ID
- `GET /api/v1/starships/search/?name={query}` - Search starships by name
- `POST /api/v1/starships/fetch` - Fetch starships from SWAPI

### Voting

- `POST /api/v1/vote/` - Vote for an entity
  - Request body: `{"entity_type": "character|film|starship", "entity_id": 1}`
- `GET /api/v1/vote/top` - Get top voted entities
  - Optional query param: `entity_type=character|film|starship`

## Running Tests

```bash
# Run tests with Docker
docker compose run --rm fastswapi pytest

# Run tests with coverage report
docker compose run --rm fastswapi pytest --cov=app --cov-report=term-missing
```

## Project Structure

```bash
FastSwapi/
├── app/
│   ├── api/           # API endpoints
│   ├── models/        # SQLAlchemy database models
│   ├── schemas/       # Pydantic validation schemas
│   ├── services/      # Business logic
│   └── utils/         # Helper functions
├── tests/             # Unit tests
├── Dockerfile
├── compose.yml
├── .env               # Environment variables
└── requirements.txt
```
