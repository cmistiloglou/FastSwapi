from fastapi import HTTPException, status
import logging
from typing import Optional
from aiohttp.client_exceptions import ClientError

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        internal_error: Optional[Exception] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.internal_error = internal_error
        super().__init__(detail)

class DatabaseError(APIError):
    """Raised when a database operation fails"""
    def __init__(self, detail: str, internal_error: Optional[Exception] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            internal_error=internal_error
        )

class ExternalAPIError(APIError):
    """Raised when an external API call fails"""
    def __init__(self, detail: str, internal_error: Optional[Exception] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            internal_error=internal_error
        )

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ValidationError(APIError):
    """Raised for validation errors"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

async def handle_external_api_error(operation):
    """Handle external API errors"""
    try:
        return await operation()
    except ClientError as e:
        logger.error(f"External API error: {str(e)}")
        raise ExternalAPIError(
            detail="Failed to communicate with external API",
            internal_error=e
        )
    except Exception as e:
        logger.error(f"Unexpected error during API call: {str(e)}")
        raise ExternalAPIError(
            detail="An unexpected error occurred",
            internal_error=e
        )