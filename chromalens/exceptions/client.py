"""
Client-related exceptions for ChromaLens client.
"""

from typing import Optional, Dict, Any


class ClientError(Exception):
    """Base exception for all client-side errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the client error.
        
        Args:
            message: Error message
            details: Additional error details if available
        """
        super().__init__(message)
        self.details = details or {}
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = f"Client Error: {super().__str__()}"
        if self.details:
            return f"{base_str} - Details: {self.details}"
        return base_str


class ConfigurationError(ClientError):
    """Exception raised for client configuration errors."""
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"Configuration Error: {super().__str__()}"


class ConnectionError(ClientError):
    """Exception raised for connection failures."""
    
    def __init__(self, message: str, host: Optional[str] = None, port: Optional[int] = None, 
                details: Optional[Dict[str, Any]] = None):
        """
        Initialize connection error.
        
        Args:
            message: Error message
            host: Host that couldn't be connected to
            port: Port that couldn't be connected to
            details: Additional error details
        """
        super().__init__(message, details)
        self.host = host
        self.port = port
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = f"Connection Error: {super().__str__()}"
        if self.host and self.port:
            return f"{base_str} - Failed to connect to {self.host}:{self.port}"
        return base_str


class TimeoutError(ClientError):
    """Exception raised for request timeouts."""
    
    def __init__(self, message: str, timeout: Optional[float] = None, 
                details: Optional[Dict[str, Any]] = None):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout: Timeout duration in seconds
            details: Additional error details
        """
        super().__init__(message, details)
        self.timeout = timeout
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = f"Timeout Error: {super().__str__()}"
        if self.timeout:
            return f"{base_str} - Request timed out after {self.timeout}s"
        return base_str


class DataError(ClientError):
    """Exception raised for errors in the data provided to the client."""
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"Data Error: {super().__str__()}"


class UnsupportedFeatureError(ClientError):
    """Exception raised when an unsupported feature is requested."""
    
    def __init__(self, message: str, feature: Optional[str] = None, 
                details: Optional[Dict[str, Any]] = None):
        """
        Initialize unsupported feature error.
        
        Args:
            message: Error message
            feature: Name of the unsupported feature
            details: Additional error details
        """
        super().__init__(message, details)
        self.feature = feature
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = f"Unsupported Feature: {super().__str__()}"
        if self.feature:
            return f"{base_str} - Feature '{self.feature}' is not supported"
        return base_str