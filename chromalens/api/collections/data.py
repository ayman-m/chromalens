"""
Collection data operations for ChromaDB.

This module handles operations for managing embeddings, metadata, and documents within collections.
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
    ENDPOINT_ADD,
    ENDPOINT_UPDATE,
    ENDPOINT_UPSERT,
    ENDPOINT_GET,
    ENDPOINT_DELETE,
    FIELD_IDS,
    FIELD_EMBEDDINGS,
    FIELD_METADATAS,
    FIELD_DOCUMENTS,
    FIELD_URIS,
    FIELD_WHERE,
    FIELD_WHERE_DOCUMENT,
    PARAM_TENANT,
    PARAM_DATABASE,
)
from chromalens.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

class CollectionDataAPI:
    """Collection data operations for ChromaDB."""
    
    def __init__(self, client: BaseClient):
        """
        Initialize with a client instance.
        
        Args:
            client: Initialized BaseClient instance
        """
        self._client = client
    
    def add(self, collection_id: str, embeddings: List[List[float]], 
           metadatas: Optional[List[Dict[str, Any]]] = None,
           documents: Optional[List[str]] = None, 
           uris: Optional[List[str]] = None,
           ids: Optional[List[str]] = None,
           database: Optional[str] = None, 
           tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Add items to a collection.
        
        Args:
            collection_id: ID of the collection
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            documents: Optional list of document strings
            uris: Optional list of URI strings
            ids: Optional list of IDs (UUIDs will be generated if not provided)
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.info(f"Adding {len(embeddings)} items to collection: {collection_id}")
        
        # Validate input lengths match
        if (metadatas and len(metadatas) != len(embeddings)) or \
           (documents and len(documents) != len(embeddings)) or \
           (uris and len(uris) != len(embeddings)) or \
           (ids and len(ids) != len(embeddings)):
            raise ValidationError("All input lists must have the same length")
        
        # Prepare payload
        payload = {
            FIELD_EMBEDDINGS: embeddings
        }
        
        if metadatas is not None:
            payload[FIELD_METADATAS] = metadatas
        
        if documents is not None:
            payload[FIELD_DOCUMENTS] = documents
            
        if uris is not None:
            payload[FIELD_URIS] = uris
            
        if ids is not None:
            payload[FIELD_IDS] = ids
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_ADD}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 add operation failed: {e}")
            # Fall back to V1
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_ADD}"
            return self._client.post(v1_endpoint, API_V1, json_data=payload)
    
    def update(self, collection_id: str, ids: List[str], 
              embeddings: Optional[List[List[float]]] = None,
              metadatas: Optional[List[Dict[str, Any]]] = None,
              documents: Optional[List[str]] = None,
              uris: Optional[List[str]] = None,
              database: Optional[str] = None, 
              tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Update items in a collection.
        
        Args:
            collection_id: ID of the collection
            ids: List of IDs to update
            embeddings: Optional list of embedding vectors
            metadatas: Optional list of metadata dictionaries
            documents: Optional list of document strings
            uris: Optional list of URI strings
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.info(f"Updating {len(ids)} items in collection: {collection_id}")
        
        # Validate that we have at least one thing to update
        if not any([embeddings, metadatas, documents, uris]):
            raise ValidationError("At least one of embeddings, metadatas, documents, or uris must be provided")
        
        # Validate input lengths match the number of IDs
        if (embeddings and len(embeddings) != len(ids)) or \
           (metadatas and len(metadatas) != len(ids)) or \
           (documents and len(documents) != len(ids)) or \
           (uris and len(uris) != len(ids)):
            raise ValidationError("All input lists must have the same length as ids")
        
        # Prepare payload
        payload = {
            FIELD_IDS: ids
        }
        
        if embeddings is not None:
            payload[FIELD_EMBEDDINGS] = embeddings
            
        if metadatas is not None:
            payload[FIELD_METADATAS] = metadatas
        
        if documents is not None:
            payload[FIELD_DOCUMENTS] = documents
            
        if uris is not None:
            payload[FIELD_URIS] = uris
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_UPDATE}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 update operation failed: {e}")
            # Fall back to V1
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_UPDATE}"
            return self._client.post(v1_endpoint, API_V1, json_data=payload)
    
    def upsert(self, collection_id: str, embeddings: List[List[float]], 
              ids: List[str],
              metadatas: Optional[List[Dict[str, Any]]] = None,
              documents: Optional[List[str]] = None,
              uris: Optional[List[str]] = None,
              database: Optional[str] = None, 
              tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Upsert items in a collection (update if exists, add if not).
        
        Args:
            collection_id: ID of the collection
            embeddings: List of embedding vectors
            ids: List of IDs to upsert
            metadatas: Optional list of metadata dictionaries
            documents: Optional list of document strings
            uris: Optional list of URI strings
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.info(f"Upserting {len(ids)} items in collection: {collection_id}")
        
        # Validate input lengths match
        if (len(embeddings) != len(ids)) or \
           (metadatas and len(metadatas) != len(ids)) or \
           (documents and len(documents) != len(ids)) or \
           (uris and len(uris) != len(ids)):
            raise ValidationError("All input lists must have the same length")
        
        # Prepare payload
        payload = {
            FIELD_EMBEDDINGS: embeddings,
            FIELD_IDS: ids
        }
        
        if metadatas is not None:
            payload[FIELD_METADATAS] = metadatas
        
        if documents is not None:
            payload[FIELD_DOCUMENTS] = documents
            
        if uris is not None:
            payload[FIELD_URIS] = uris
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_UPSERT}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 upsert operation failed: {e}")
            # Fall back to V1
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_UPSERT}"
            return self._client.post(v1_endpoint, API_V1, json_data=payload)
    
    def get(self, collection_id: str, ids: Optional[List[str]] = None,
           where: Optional[Dict[str, Any]] = None,
           where_document: Optional[Dict[str, Any]] = None,
           limit: Optional[int] = None,
           offset: Optional[int] = None,
           include: Optional[List[str]] = None,
           database: Optional[str] = None, 
           tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Get items from a collection.
        
        Args:
            collection_id: ID of the collection
            ids: Optional list of specific IDs to retrieve
            where: Optional filter conditions on metadata
            where_document: Optional filter conditions on documents
            limit: Maximum number of results to return
            offset: Offset for pagination
            include: List of fields to include (metadatas, documents, embeddings)
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response with matching items
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.debug(f"Getting items from collection: {collection_id}")
        
        # Prepare payload
        payload = {}
        
        if ids is not None:
            payload[FIELD_IDS] = ids
            
        if where is not None:
            payload[FIELD_WHERE] = where
            
        if where_document is not None:
            payload[FIELD_WHERE_DOCUMENT] = where_document
            
        if limit is not None:
            payload["limit"] = limit
            
        if offset is not None:
            payload["offset"] = offset
            
        if include is not None:
            payload["include"] = include
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_GET}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 get operation failed: {e}")
            # Fall back to V1
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_GET}"
            return self._client.post(v1_endpoint, API_V1, json_data=payload)
    
    def delete(self, collection_id: str, ids: Optional[List[str]] = None,
              where: Optional[Dict[str, Any]] = None,
              where_document: Optional[Dict[str, Any]] = None,
              database: Optional[str] = None, 
              tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete items from a collection.
        
        Args:
            collection_id: ID of the collection
            ids: Optional list of specific IDs to delete
            where: Optional filter conditions on metadata
            where_document: Optional filter conditions on documents
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        
        # Need at least one of ids, where, or where_document
        if ids is None and where is None and where_document is None:
            raise ValidationError("At least one of ids, where, or where_document must be provided")
        
        # Log appropriately based on what's being deleted
        if ids is not None:
            logger.info(f"Deleting {len(ids)} specific items from collection: {collection_id}")
        else:
            logger.info(f"Deleting items matching filters from collection: {collection_id}")
        
        # Prepare payload
        payload = {}
        
        if ids is not None:
            payload[FIELD_IDS] = ids
            
        if where is not None:
            payload[FIELD_WHERE] = where
            
        if where_document is not None:
            payload[FIELD_WHERE_DOCUMENT] = where_document
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_DELETE}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 delete operation failed: {e}")
            # Fall back to V1
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_DELETE}"
            return self._client.post(v1_endpoint, API_V1, json_data=payload)