"""
Base client module handling core HTTP interactions with ChromaDB API.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union, Tuple
from urllib.parse import urljoin

from chromalens.exceptions.api import APIError, NotFoundError, AuthenticationError
from chromalens.exceptions.client import ClientError
from chromalens.config.settings import DEFAULT_TIMEOUT, DEFAULT_CHUNK_SIZE
from chromalens.config.constants import API_V1, API_V2

logger = logging.getLogger(__name__)


class BaseClient:
    """
    Base client for ChromaDB API handling HTTP requests, authentication, and error handling.
    
    This class isn't meant to be used directly, but serves as a foundation for the main
    ChromaLensClient class.
    """
    
    def __init__(
        self, 
        host: str = "localhost",
        port: int = 8008,
        tenant: str = "default_tenant",
        database: str = "default_database",
        ssl: bool = False,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ):
        """
        Initialize the base client.
        
        Args:
            host: ChromaDB server hostname or IP
            port: ChromaDB server port
            tenant: Default tenant name to use for operations
            database: Default database name to use for operations
            ssl: Whether to use HTTPS instead of HTTP
            headers: Additional headers to include in all requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.host = host
        self.port = port
        self.tenant = tenant
        self.database = database
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        # Construct the base URL
        protocol = "https" if ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}"
        # Initialize headers with defaults
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        # Add user-provided headers
        if headers:
            self.headers.update(headers)
    
    def _validate_response(self, response: requests.Response) -> None:
        """
        Validate response status code and handle errors.
        
        Args:
            response: The HTTP response to validate
            
        Raises:
            NotFoundError: If resource doesn't exist (404)
            AuthenticationError: If authentication failed (401/403)
            APIError: For other API errors
        """
        if response.status_code >= 400:
            error_msg = f"Request failed with status {response.status_code}"
            
            # Try to extract error details from response
            try:
                error_detail = response.json().get('detail', '')
                if error_detail:
                    error_msg += f": {error_detail}"
            except (ValueError, KeyError):
                # If we can't parse the JSON or find 'detail', use text
                if response.text:
                    error_msg += f": {response.text}"
            
            # Raise appropriate error based on status code
            if response.status_code == 404:
                raise NotFoundError(error_msg)
            elif response.status_code in (401, 403):
                raise AuthenticationError(error_msg)
            else:
                raise APIError(error_msg, status_code=response.status_code)
    
    def _build_url(self, endpoint: str, api_version: str = API_V2) -> str:
        """
        Build a full URL for the API endpoint.
        
        Args:
            endpoint: API endpoint path (without leading slash)
            api_version: API version to use (v1 or v2)
            
        Returns:
            Full URL for the API endpoint
        """
        # Ensure endpoint doesn't start with slash
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
        # Build the URL with appropriate API version
        url = urljoin(self.base_url, f"/api/{api_version}/{endpoint}")
        return url

    def _request(
        self,
        method: str,
        endpoint: str,
        api_version: str = API_V2,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Make a request to the ChromaDB API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            api_version: API version to use (v1 or v2)
            params: URL parameters
            data: Request body data
            json_data: JSON data for request body
            headers: Additional headers for this request
            timeout: Request timeout override
            
        Returns:
            Parsed JSON response
            
        Raises:
            ClientError: For client-side errors
            APIError: For server-side errors
        """
        url = self._build_url(endpoint, api_version)
        
        # Merge default headers with request-specific headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.timeout
        
        try:
            logger.debug(f"Making {method} request to {url}")
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=timeout,
                verify=self.verify_ssl
            )
            # Check for errors
            self._validate_response(response)
            
            # Return parsed JSON if available, otherwise return raw response
            if response.content and response.headers.get('Content-Type') == 'application/json':
                return response.json()
            elif response.content:
                return response.content
            return None
            
        except requests.RequestException as e:
            # Convert requests exceptions to our custom exception
            raise ClientError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, api_version: str = API_V2, **kwargs) -> Any:
        """Make a GET request to the API."""
        return self._request('GET', endpoint, api_version, **kwargs)
    
    def post(self, endpoint: str, api_version: str = API_V2, **kwargs) -> Any:
        """Make a POST request to the API."""
        return self._request('POST', endpoint, api_version, **kwargs)
    
    def put(self, endpoint: str, api_version: str = API_V2, **kwargs) -> Any:
        """Make a PUT request to the API."""
        return self._request('PUT', endpoint, api_version, **kwargs)
    
    def delete(self, endpoint: str, api_version: str = API_V2, **kwargs) -> Any:
        """Make a DELETE request to the API."""
        return self._request('DELETE', endpoint, api_version, **kwargs)
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Check server heartbeat to verify connectivity.
        
        Returns:
            Dictionary with server heartbeat information
        """
        return self.get('heartbeat')
    
    def version(self) -> str:
        """
        Get server version information.
        
        Returns:
            Version string
        """
        return self.get('version')
    
    def reset(self) -> bool:
        """
        Reset the ChromaDB server (warning: destructive operation).
        
        Returns:
            True if reset was successful
        """
        return self.post('reset')