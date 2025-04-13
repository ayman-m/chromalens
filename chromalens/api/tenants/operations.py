"""
Tenant operations for ChromaDB.

This module handles tenant-related operations like listing, creating, and getting tenants.
"""

import logging
from typing import Dict, List, Any, Optional

from chromalens.client.base import BaseClient
from chromalens.config.constants import (
    API_V1,
    API_V2,
    ENDPOINT_TENANTS,
    FIELD_NAME,
)
from chromalens.exceptions import NotFoundError

logger = logging.getLogger(__name__)

class TenantsAPI:
    """Tenant operations for ChromaDB."""
    
    def __init__(self, client: BaseClient):
        """
        Initialize with a client instance.
        
        Args:
            client: Initialized BaseClient instance
        """
        self._client = client
    
    def list(self) -> List[Dict[str, Any]]:
        """
        List all tenants.
        
        Returns:
            List of tenant objects
        """
        logger.debug("Listing all tenants")
        # Try v2 first
        try:
            return self._client.get(ENDPOINT_TENANTS, API_V2)
        except Exception as e:
            logger.debug(f"V2 tenant listing failed: {e}")
            # Fall back to V1
            return self._client.get(ENDPOINT_TENANTS, API_V1)
    
    def create(self, name: str) -> Dict[str, Any]:
        """
        Create a new tenant.
        
        Args:
            name: Name of the tenant to create
            
        Returns:
            Created tenant object
        """
        logger.info(f"Creating tenant: {name}")
        payload = {FIELD_NAME: name}
        
        # Try v2 first
        try:
            return self._client.post(ENDPOINT_TENANTS, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 tenant creation failed: {e}")
            # Fall back to V1
            return self._client.post(ENDPOINT_TENANTS, API_V1, json_data=payload)
    
    def get(self, name: str) -> Dict[str, Any]:
        """
        Get information about a tenant.
        
        Args:
            name: Name of the tenant
            
        Returns:
            Tenant object
        """
        logger.debug(f"Getting tenant: {name}")
        endpoint = f"{ENDPOINT_TENANTS}/{name}"
        
        # Try v2 first
        try:
            return self._client.get(endpoint, API_V2)
        except NotFoundError:
            # Don't try V1 if the tenant doesn't exist in V2
            raise
        except Exception as e:
            logger.debug(f"V2 tenant retrieval failed: {e}")
            # Fall back to V1
            return self._client.get(endpoint, API_V1)