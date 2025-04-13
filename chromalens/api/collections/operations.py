"""
Collection operations for ChromaDB.

This module handles collection-related operations like listing, creating, getting and deleting collections.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from chromalens.client.base import BaseClient
from chromalens.config.constants import (
    API_V1,
    API_V2,
    ENDPOINT_TENANTS,
    ENDPOINT_DATABASES,
    ENDPOINT_COLLECTIONS,
    FIELD_NAME,
    FIELD_METADATA,
    FIELD_DIMENSION,
    PARAM_TENANT,
    PARAM_DATABASE,
    PARAM_LIMIT,
    PARAM_OFFSET,
)
from chromalens.exceptions import NotFoundError, APIError

logger = logging.getLogger(__name__)

class CollectionsAPI:
    """Collection operations for ChromaDB."""
    
    def __init__(self, client: BaseClient):
        """
        Initialize with a client instance.
        
        Args:
            client: Initialized BaseClient instance
        """
        self._client = client
    
    def list(self, database: Optional[str] = None, tenant: Optional[str] = None,
            limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all collections in a database.
        
        Args:
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            limit: Maximum number of collections to return
            offset: Offset for pagination
            
        Returns:
            List of collection objects
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.debug(f"Listing collections in database: {database} for tenant: {tenant}")
        
        # Prepare parameters
        params = {}
        if limit is not None:
            params[PARAM_LIMIT] = limit
        if offset is not None:
            params[PARAM_OFFSET] = offset
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}"
            return self._client.get(v2_endpoint, API_V2, params=params)
        except Exception as e:
            logger.debug(f"V2 collection listing failed: {e}")
            # Fall back to V1 - this uses tenant and database as query parameters
            v1_params = {
                PARAM_TENANT: tenant,
                PARAM_DATABASE: database
            }
            if params:
                v1_params.update(params)
            return self._client.get(ENDPOINT_COLLECTIONS, API_V1, params=v1_params)
    
    def create(self, name: str, metadata: Optional[Dict[str, Any]] = None,
              dimension: Optional[int] = None, get_or_create: bool = False,
              database: Optional[str] = None, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new collection.
        
        Args:
            name: Name of the collection to create
            metadata: Optional metadata for the collection
            dimension: Vector dimension (default is server-defined, usually 768)
            get_or_create: If True, return existing collection if it exists
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Created collection object
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.info(f"Creating collection: {name} in database: {database} for tenant: {tenant}")
        
        # Prepare payload
        payload = {
            FIELD_NAME: name,
            "get_or_create": get_or_create
        }
        
        if metadata is not None:
            payload[FIELD_METADATA] = metadata
            
        if dimension is not None:
            payload[FIELD_DIMENSION] = dimension
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 collection creation failed: {e}")
            # Fall back to V1 - this uses tenant and database as query parameters
            params = {
                PARAM_TENANT: tenant,
                PARAM_DATABASE: database
            }
            return self._client.post(ENDPOINT_COLLECTIONS, API_V1, params=params, json_data=payload)
    
    def get(self, name: str, database: Optional[str] = None, 
           tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a collection by name.
        
        Args:
            name: Name of the collection
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Collection object
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.debug(f"Getting collection: {name} in database: {database} for tenant: {tenant}")
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{name}"
            return self._client.get(v2_endpoint, API_V2)
        except NotFoundError:
            # Don't try V1 if the collection doesn't exist in V2
            raise
        except Exception as e:
            logger.debug(f"V2 collection retrieval failed: {e}")
            # Fall back to V1 - this uses tenant and database as query parameters
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{name}"
            params = {
                PARAM_TENANT: tenant,
                PARAM_DATABASE: database
            }
            return self._client.get(v1_endpoint, API_V1, params=params)
    
    def get_by_id(self, collection_id: str, database: Optional[str] = None,
                 tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a collection by ID.
        
        Args:
            collection_id: ID of the collection
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Collection object
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.debug(f"Getting collection by ID: {collection_id} in database: {database} for tenant: {tenant}")
        
        # List all collections and find the one with matching ID
        collections = self.list(database, tenant)
        for collection in collections:
            if collection.get("id") == collection_id:
                return collection
        
        # If no collection with this ID is found
        raise NotFoundError(f"Collection with ID {collection_id} not found")
    
    def delete(self, name: str, database: Optional[str] = None,
              tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a collection by name.
        
        Args:
            name: Name of the collection to delete
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.info(f"Deleting collection: {name} in database: {database} for tenant: {tenant}")
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{name}"
            return self._client.delete(v2_endpoint, API_V2)
        except NotFoundError:
            # Don't try V1 if the collection doesn't exist in V2
            raise
        except Exception as e:
            logger.debug(f"V2 collection deletion failed: {e}")
            # Fall back to V1 - this uses tenant and database as query parameters
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{name}"
            params = {
                PARAM_TENANT: tenant,
                PARAM_DATABASE: database
            }
            return self._client.delete(v1_endpoint, API_V1, params=params)
    
    def update(self, collection_id: str, new_name: Optional[str] = None,
              new_metadata: Optional[Dict[str, Any]] = None, database: Optional[str] = None,
              tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a collection.
        
        Args:
            collection_id: ID of the collection to update
            new_name: New name for the collection
            new_metadata: New metadata for the collection
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Updated collection object
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        
        update_fields = {}
        if new_name is not None:
            update_fields["new_name"] = new_name
        if new_metadata is not None:
            update_fields["new_metadata"] = new_metadata
            
        if not update_fields:
            raise ValueError("At least one of new_name or new_metadata must be provided")
            
        logger.info(f"Updating collection with ID: {collection_id} in database: {database} for tenant: {tenant}")
        
        # Only available in v2 API - no fallback
        v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}"
        return self._client.put(v2_endpoint, API_V2, json_data=update_fields)
    
    def count(self, collection_id: str, database: Optional[str] = None,
             tenant: Optional[str] = None) -> int:
        """
        Count items in a collection.
        
        Args:
            collection_id: ID of the collection
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Number of items in the collection
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.debug(f"Counting items in collection: {collection_id}")
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/count"
            return self._client.get(v2_endpoint, API_V2)
        except Exception as e:
            logger.debug(f"V2 collection count failed: {e}")
            # Fall back to V1
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{collection_id}/count"
            return self._client.get(v1_endpoint, API_V1)