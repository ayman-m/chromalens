"""
System-level API operations for ChromaDB.

This module handles operations like heartbeat, version check, reset, etc.
"""

import logging
from typing import Dict, Any, Optional, Union

from chromalens.client.base import BaseClient
from chromalens.config.constants import (
    API_V1, 
    API_V2,
    ENDPOINT_HEARTBEAT,
    ENDPOINT_VERSION,
    ENDPOINT_RESET,
    ENDPOINT_PRE_FLIGHT_CHECKS,
)

logger = logging.getLogger(__name__)

class SystemAPI:
    """System-level API operations for ChromaDB."""
    
    def __init__(self, client: BaseClient):
        """
        Initialize with a client instance.
        
        Args:
            client: Initialized BaseClient instance
        """
        self._client = client
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Check server heartbeat to verify connectivity.
        
        Returns:
            Dictionary with server heartbeat information
        """
        logger.debug("Checking server heartbeat")
        # Try v2 first, fall back to v1 if needed
        try:
            return self._client.get(ENDPOINT_HEARTBEAT, API_V2)
        except Exception as e:
            logger.debug(f"V2 heartbeat failed, trying V1: {e}")
            return self._client.get(ENDPOINT_HEARTBEAT, API_V1)
    
    def version(self) -> str:
        """
        Get server version information.
        
        Returns:
            Version string
        """
        logger.debug("Getting server version")
        # Try v2 first, fall back to v1 if needed
        try:
            return self._client.get(ENDPOINT_VERSION, API_V2)
        except Exception as e:
            logger.debug(f"V2 version check failed, trying V1: {e}")
            return self._client.get(ENDPOINT_VERSION, API_V1)
    
    def reset(self) -> bool:
        """
        Reset the ChromaDB server (warning: destructive operation).
        This will delete all data in the server.
        
        Returns:
            True if reset was successful
        """
        logger.warning("Resetting ChromaDB server (all data will be deleted)")
        # Try v2 first, fall back to v1 if needed
        try:
            return self._client.post(ENDPOINT_RESET, API_V2)
        except Exception as e:
            logger.debug(f"V2 reset failed, trying V1: {e}")
            return self._client.post(ENDPOINT_RESET, API_V1)
    
    def pre_flight_checks(self) -> Dict[str, Any]:
        """
        Run pre-flight checks to verify server functionality.
        
        Returns:
            Dictionary with pre-flight check results
        """
        logger.debug("Running pre-flight checks")
        # Try v2 first, fall back to v1 if needed
        try:
            return self._client.get(ENDPOINT_PRE_FLIGHT_CHECKS, API_V2)
        except Exception as e:
            logger.debug(f"V2 pre-flight checks failed, trying V1: {e}")
            return self._client.get(ENDPOINT_PRE_FLIGHT_CHECKS, API_V1)