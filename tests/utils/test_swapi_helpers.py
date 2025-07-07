# tests/utils/test_swapi_helpers.py
from app.utils.swapi_helpers import extract_swapi_id


def test_extract_swapi_id():
    """Test extracting IDs from SWAPI URLs"""
    # Valid URLs
    assert extract_swapi_id("https://swapi.info/api/people/1/") == 1
    assert extract_swapi_id("https://swapi.info/api/films/5/") == 5
    assert extract_swapi_id("https://swapi.info/api/starships/10/") == 10

    # URL without trailing slash
    assert extract_swapi_id("https://swapi.info/api/planets/3") == 3

    # Invalid URLs
    assert extract_swapi_id("not-a-url") is None
    assert extract_swapi_id("https://swapi.info/api/people/abc/") is None
    assert extract_swapi_id("https://example.com/1/") is None
