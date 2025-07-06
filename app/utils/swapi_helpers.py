import re
from typing import Optional


def extract_swapi_id(url: str) -> Optional[int]:
    """
    Extracts the numeric ID from a SWAPI resource URL.
    Example: 'https://swapi.dev/api/people/1/' → 1
    """
    match = re.search(r"/api/\w+/(?P<id>\d+)/?$", url)
    return int(match.group("id")) if match else None
