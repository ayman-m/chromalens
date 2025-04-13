"""
Collection query operations for ChromaDB.

This module handles operations for querying and searching collections.
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
    ENDPOINT_QUERY,
    FIELD_WHERE,
    FIELD_WHERE_DOCUMENT,
    FIELD_N_RESULTS,
)
from chromalens.exceptions import ValidationError

logger = logging.getLogger(__name__)

class CollectionQueryAPI:
    """Collection query operations for ChromaDB."""
    
    def __init__(self, client: BaseClient):
        """
        Initialize with a client instance.
        
        Args:
            client: Initialized BaseClient instance
        """
        self._client = client
    
    def query(self, collection_id: str, query_embeddings: List[List[float]],
             n_results: int = 10,
             where: Optional[Dict[str, Any]] = None,
             where_document: Optional[Dict[str, Any]] = None,
             include: Optional[List[str]] = None,
             database: Optional[str] = None, 
             tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Query a collection for nearest neighbors.
        
        Args:
            collection_id: ID of the collection
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return per query
            where: Optional filter conditions on metadata
            where_document: Optional filter conditions on documents
            include: List of fields to include (metadatas, documents, distances)
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Query results with nearest neighbors
        """
        tenant = tenant or self._client.tenant
        database = database or self._client.database
        logger.info(f"Querying collection {collection_id} with {len(query_embeddings)} embeddings, requesting {n_results} results per query")
        
        # Validate inputs
        if not query_embeddings:
            raise ValidationError("query_embeddings cannot be empty")
            
        # Prepare payload
        payload = {
            "query_embeddings": query_embeddings,
            FIELD_N_RESULTS: n_results
        }
        
        if where is not None:
            payload[FIELD_WHERE] = where
            
        if where_document is not None:
            payload[FIELD_WHERE_DOCUMENT] = where_document
            
        if include is not None:
            payload["include"] = include
        
        # Try v2 first - this uses tenant and database in the path
        try:
            v2_endpoint = f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_QUERY}"
            return self._client.post(v2_endpoint, API_V2, json_data=payload)
        except Exception as e:
            logger.debug(f"V2 query operation failed: {e}")
            # Fall back to V1
            v1_endpoint = f"{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_QUERY}"
            return self._client.post(v1_endpoint, API_V1, json_data=payload)
    
    def text_query(self, collection_id: str, query_texts: List[str],
                 n_results: int = 10,
                 where: Optional[Dict[str, Any]] = None,
                 where_document: Optional[Dict[str, Any]] = None,
                 include: Optional[List[str]] = None,
                 embedding_function: Optional[callable] = None,
                 database: Optional[str] = None, 
                 tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Query a collection using text queries that get converted to embeddings.
        
        Args:
            collection_id: ID of the collection
            query_texts: List of text queries
            n_results: Number of results to return per query
            where: Optional filter conditions on metadata
            where_document: Optional filter conditions on documents
            include: List of fields to include (metadatas, documents, distances)
            embedding_function: Function to convert text to embeddings (required)
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Query results with nearest neighbors
        """
        if embedding_function is None:
            raise ValueError("embedding_function must be provided to convert text to embeddings")
            
        # Convert text queries to embeddings
        query_embeddings = embedding_function(query_texts)
        
        # Call the standard query method
        return self.query(
            collection_id=collection_id,
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include,
            database=database,
            tenant=tenant
        )