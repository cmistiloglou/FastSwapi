import aiohttp
import re
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SWAPI_BASE_URL = os.getenv("SWAPI_BASE_URL", "https://swapi.info/api")


class SwapiService:
    """Service for interacting with the Star Wars API (SWAPI)"""

    def __init__(self, base_url: str = SWAPI_BASE_URL):
        self.base_url = base_url
        self.session = None

    async def _ensure_session(self):
        """Ensure HTTP session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    def _extract_id_from_url(self, url: str) -> int:
        """Extract the ID from SWAPI URL"""
        match = re.search(r"/(\d+)/?\$", url)
        if match:
            return int(match.group(1))
        return 0

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _get_resource(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a resource from SWAPI with retry logic"""
        session = await self._ensure_session()
        url = f"{self.base_url}/{endpoint}"

        async with session.get(url, params=params) as response:
            if response.status != 200:
                response.raise_for_status()
            return await response.json()

    async def get_all_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """Get all resources of a specific type"""
        data = await self._get_resource(resource_type)

        if not isinstance(data, list):
            raise TypeError(f"Expected list of resources, got: {type(data).__name__}")

        return data

    async def get_characters(self) -> List[Dict[str, Any]]:
        """Get all characters from SWAPI"""
        characters = await self.get_all_resources("people")
        for character in characters:
            character["swapi_id"] = self._extract_id_from_url(character["url"])
        return characters

    async def get_films(self) -> List[Dict[str, Any]]:
        """Get all films from SWAPI"""
        films = await self.get_all_resources("films")
        for film in films:
            film["swapi_id"] = self._extract_id_from_url(film["url"])
        return films

    async def get_starships(self) -> List[Dict[str, Any]]:
        """Get all starships from SWAPI"""
        starships = await self.get_all_resources("starships")
        for starship in starships:
            starship["swapi_id"] = self._extract_id_from_url(starship["url"])
        return starships

    async def search_resource(
        self, resource_type: str, search_query: str
    ) -> List[Dict[str, Any]]:
        """Search for resources by name/title"""
        data = await self._get_resource(resource_type, {"search": search_query})
        results = data["results"]
        for item in results:
            item["swapi_id"] = self._extract_id_from_url(item["url"])
        return results
