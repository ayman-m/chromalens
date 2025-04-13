"""
Exceptions module for ChromaLens client.
"""

from chromalens.exceptions.api import (
    APIError,
    NotFoundError,
    AuthenticationError,
    ValidationError,
    ServerError,
    RateLimitError,
    ConflictError,
)

from chromalens.exceptions.client import (
    ClientError,
    ConfigurationError,
    ConnectionError,
    TimeoutError,
    DataError,
    UnsupportedFeatureError,
)

__all__ = [
    # API Errors
    'APIError',
    'NotFoundError',
    'AuthenticationError',
    'ValidationError',
    'ServerError',
    'RateLimitError',
    'ConflictError',
    
    # Client Errors
    'ClientError',
    'ConfigurationError',
    'ConnectionError',
    'TimeoutError',
    'DataError',
    'UnsupportedFeatureError',
]