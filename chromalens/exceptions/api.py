"""
API-related exceptions for ChromaLens client.
"""

from typing import Optional, Dict, Any


class APIError(Exception):
    """Base exception for all API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Any = None):
        """
        Initialize the API error.
        
        Args:
            message: Error message
            status_code: HTTP status code if available
            response: Raw API response if available
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.status_code:
            return f"API Error (Status {self.status_code}): {super().__str__()}"
        return f"API Error: {super().__str__()}"


class NotFoundError(APIError):
    """Exception raised when a resource is not found (HTTP 404)."""
    
    def __init__(self, message: str, response: Any = None):
        """Initialize not found error with status code 404."""
        super().__init__(message, status_code=404, response=response)
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"Not Found: {super().__str__()}"


class AuthenticationError(APIError):
    """Exception raised for authentication failures (HTTP 401/403)."""
    
    def __init__(self, message: str, status_code: Optional[int] = 401, response: Any = None):
        """Initialize authentication error with status code 401 or 403."""
        super().__init__(message, status_code=status_code, response=response)
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"Authentication Error: {super().__str__()}"


class ValidationError(APIError):
    """Exception raised for validation errors (HTTP 400/422)."""
    
    def __init__(self, 
                 message: str, 
                 status_code: Optional[int] = 422, 
                 response: Any = None, 
                 validation_errors: Optional[Dict[str, Any]] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            status_code: HTTP status code (default 422)
            response: Raw API response
            validation_errors: Detailed validation errors if available
        """
        super().__init__(message, status_code=status_code, response=response)
        self.validation_errors = validation_errors or {}
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = f"Validation Error: {super().__str__()}"
        if self.validation_errors:
            return f"{base_str} - Details: {self.validation_errors}"
        return base_str


class ServerError(APIError):
    """Exception raised for server errors (HTTP 5xx)."""
    
    def __init__(self, message: str, status_code: Optional[int] = 500, response: Any = None):
        """Initialize server error with status code 500."""
        super().__init__(message, status_code=status_code, response=response)
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"Server Error: {super().__str__()}"


class RateLimitError(APIError):
    """Exception raised when rate limit is exceeded (HTTP 429)."""
    
    def __init__(self, 
                 message: str, 
                 response: Any = None, 
                 retry_after: Optional[int] = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            response: Raw API response
            retry_after: Seconds to wait before retrying (if provided)
        """
        super().__init__(message, status_code=429, response=response)
        self.retry_after = retry_after
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = f"Rate Limit Exceeded: {super().__str__()}"
        if self.retry_after:
            return f"{base_str} - Retry after {self.retry_after} seconds"
        return base_str


class ConflictError(APIError):
    """Exception raised for resource conflicts (HTTP 409)."""
    
    def __init__(self, message: str, response: Any = None):
        """Initialize conflict error with status code 409."""
        super().__init__(message, status_code=409, response=response)
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"Resource Conflict: {super().__str__()}"