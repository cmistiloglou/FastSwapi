# tests/utils/test_error_handling.py
import pytest
from aiohttp.client_exceptions import ClientError
from fastapi import status

from app.utils.error_handling import (
    APIError,
    DatabaseError,
    ExternalAPIError,
    NotFoundError,
    ValidationError,
    handle_external_api_error,
)


def test_api_error_classes():
    """Test the error classes"""
    # Base APIError
    error = APIError(status_code=418, detail="I'm a teapot")
    assert error.status_code == 418
    assert error.detail == "I'm a teapot"

    # DatabaseError
    db_error = DatabaseError(detail="Database connection failed")
    assert db_error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert db_error.detail == "Database connection failed"

    # NotFoundError
    not_found = NotFoundError(detail="Character not found")
    assert not_found.status_code == status.HTTP_404_NOT_FOUND
    assert not_found.detail == "Character not found"

    # ValidationError
    validation = ValidationError(detail="Invalid input")
    assert validation.status_code == status.HTTP_400_BAD_REQUEST
    assert validation.detail == "Invalid input"


@pytest.mark.asyncio
async def test_handle_external_api_error():
    """Test the external API error handler"""

    # Test successful operation
    async def success_operation():
        return "success"

    result = await handle_external_api_error(success_operation)
    assert result == "success"

    # Test ClientError handling
    async def failed_operation():
        raise ClientError("API connection failed")

    with pytest.raises(ExternalAPIError) as exc_info:
        await handle_external_api_error(failed_operation)

    assert "Failed to communicate with external API" in exc_info.value.detail
    assert isinstance(exc_info.value.internal_error, ClientError)
