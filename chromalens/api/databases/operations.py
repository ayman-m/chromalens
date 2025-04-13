"""
Database operations for ChromaDB.

This module handles database-related operations like listing, creating, getting, and deleting databases.
"""

import logging
from typing import Dict, List, Any, Optional

from chromalens.client.base import BaseClient
from chromalens.config.constants import (
    API_V1,
    API_V2,
    ENDPOINT_TENANTS,
    ENDPOINT_DATABASES,
    FIELD_NAME,
    PARAM_TENANT,
    PARAM_LIMIT,
    PARAM_OFFSET,
)
from chromalens.exceptions import NotFoundError

logger = logging.getLogger(__name__)

class DatabasesAPI:
    """Database operations for ChromaDB."""
    
    def __init__(self, client: BaseClient):
        """
        Initialize with a client instance.
        
        Args:
            client: Initialized BaseClient instance
        """
        self._client = client
    
    def list(self, tenant: Optional[str] = None, limit: Optional[int] = None, 
            offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all databases for a tenant.
        
        Args:
            tenant: Tenant name (defaults to client's default tenant)
            limit: Maximum number of databases to return
            offset: Offset for pagination
            
        Returns:
            List of database objects
        """
        tenant = tenant or self._client.tenant
        logger.debug(f"Listing databases for tenant: {tenant}")
        
        # Prepare parameters
        params = {}
        if limit is not None:
            params[PARAM_LIMIT] = limit
        if offset is not None:
            params[PARAM_OFFSET] = offset
            
        # Try v2 first - this uses the tenant in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}"
            return self._client.get(v2_endpoint, API_V2, params=params)
        except Exception as e:
            logger.debug(f"V2 database listing failed: {e}")
            # Fall back to V1 - this uses the tenant as a query parameter
            v1_params = {PARAM_TENANT: tenant}
            if params:
                v1_params.update(params)
            return self._client.get(ENDPOINT_DATABASES, API_V1, params=v1_params)
    
    def create(self, name: str, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new database.
        
        Args:
            name: Name of the database to create
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Created database object
        """
        tenant = tenant or self._client.tenant
        logger.info(f"Creating database: {name} for tenant: {tenant}")
        
        payload = {FIELD_NAME: name}
        
        # Try v2 first - this uses the tenant in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 database creation failed: {e}")
            # Fall back to V1 - this uses the tenant as a query parameter
            params = {PARAM_TENANT: tenant}
            return self._client.post(ENDPOINT_DATABASES, API_V1, params=params, json_data=payload)
    
    def get(self, name: str, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a database.
        
        Args:
            name: Name of the database
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Database object
        """
        tenant = tenant or self._client.tenant
        logger.debug(f"Getting database: {name} for tenant: {tenant}")
        
        # Try v2 first - this uses the tenant in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{name}"
            return self._client.get(v2_endpoint, API_V2)
        except NotFoundError:
            # Don't try V1 if the database doesn't exist in V2
            raise
        except Exception as e:
            logger.debug(f"V2 database retrieval failed: {e}")
            # Fall back to V1 - this uses the tenant as a query parameter
            v1_endpoint = f"{ENDPOINT_DATABASES}/{name}"
            params = {PARAM_TENANT: tenant}
            return self._client.get(v1_endpoint, API_V1, params=params)
    
    def delete(self, name: str, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a database.
        
        Args:
            name: Name of the database to delete
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self._client.tenant
        logger.info(f"Deleting database: {name} for tenant: {tenant}")
        
        # Try v2 first - this uses the tenant in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{name}"
            return self._client.delete(v2_endpoint, API_V2)
        except NotFoundError:
            # Don't try V1 if the database doesn't exist in V2
            raise
        except Exception as e:
            logger.debug(f"V2 database deletion failed: {e}")
            # Fall back to V1 - this uses the tenant as a query parameter
            v1_endpoint = f"{ENDPOINT_DATABASES}/{name}"
            params = {PARAM_TENANT: tenant}
            return self._client.delete(v1_endpoint, API_V1, params=params)
    
    def count_collections(self, database_name: Optional[str] = None, 
                         tenant: Optional[str] = None) -> int:
        """
        Count collections in a database.
        
        Args:
            database_name: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Number of collections in the database
        """
        tenant = tenant or self._client.tenant
        database_name = database_name or self._client.database
        logger.debug(f"Counting collections in database: {database_name} for tenant: {tenant}")
        
        # This endpoint is only available in v2
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database_name}/collections_count"
            return self._client.get(v2_endpoint, API_V2)
        except Exception as e:
            logger.debug(f"V2 collections count failed: {e}")
            # Fall back to getting the list and counting it
            try:
                collections = self.get_collections(database_name, tenant)
                return len(collections)
            except Exception as e2:
                logger.error(f"Failed to count collections: {e2}")
                raise
    
    def get_collections(self, database_name: Optional[str] = None, 
                       tenant: Optional[str] = None, 
                       limit: Optional[int] = None,
                       offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all collections in a database.
        
        Args:
            database_name: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            limit: Maximum number of collections to return
            offset: Offset for pagination
            
        Returns:
            List of collection objects
        """
        from chromalens.api.collections.operations import CollectionsAPI
        collections_api = CollectionsAPI(self._client)
        return collections_api.list(database_name, tenant, limit, offset)