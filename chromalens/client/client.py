"""
Main ChromaLens client implementation.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

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
    ENDPOINT_COUNT,
    ENDPOINT_QUERY,
    FIELD_NAME,
    FIELD_ID,
    FIELD_METADATA,
    FIELD_DIMENSION,
    FIELD_IDS,
    FIELD_EMBEDDINGS,
    FIELD_METADATAS,
    FIELD_DOCUMENTS,
    FIELD_WHERE,
    FIELD_WHERE_DOCUMENT,
    FIELD_N_RESULTS,
    FIELD_INCLUDE,
    PARAM_TENANT,
    PARAM_DATABASE,
    PARAM_LIMIT,
    PARAM_OFFSET,
)
from chromalens.exceptions import ClientError, ConfigurationError
from chromalens.config.settings import get_settings

logger = logging.getLogger(__name__)


class ChromaLensClient(BaseClient):
    """
    Main client for interacting with ChromaDB API.
    
    This client provides high-level methods for managing tenants, databases,
    collections, and performing operations like adding, querying, and managing
    vector embeddings.
    """
    
    def __init__(
        self, 
        host: Optional[str] = None,
        port: Optional[int] = None,
        tenant: Optional[str] = None,
        database: Optional[str] = None,
        ssl: Optional[bool] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        verify_ssl: Optional[bool] = None,
    ):
        """
        Initialize the ChromaLens client.
        
        Args:
            host: ChromaDB server hostname or IP
            port: ChromaDB server port
            tenant: Default tenant name to use for operations
            database: Default database name to use for operations
            ssl: Whether to use HTTPS instead of HTTP
            api_key: API key for authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        # Build settings from defaults, environment, and explicit params
        settings = get_settings()
        
        # Override with any explicitly provided parameters
        if host is not None:
            settings["host"] = host
        if port is not None:
            settings["port"] = port
        if tenant is not None:
            settings["tenant"] = tenant
        if database is not None:
            settings["database"] = database
        if ssl is not None:
            settings["ssl"] = ssl
        if timeout is not None:
            settings["timeout"] = timeout
        if verify_ssl is not None:
            settings["verify_ssl"] = verify_ssl
        
        # Add API key to headers if provided
        headers = {}
        if api_key or settings.get("api_key"):
            key = api_key or settings.get("api_key")
            headers["Authorization"] = f"Bearer {key}"
        
        # Initialize the base client
        super().__init__(
            host=settings["host"],
            port=settings["port"],
            tenant=settings.get("tenant", "default_tenant"),
            database=settings.get("database", "default_database"),
            ssl=settings.get("ssl", False),
            headers=headers,
            timeout=settings.get("timeout"),
            verify_ssl=settings.get("verify_ssl", True),
        )
        
        # Test connection during initialization if verify_connection is True
        self._verify_connection()
    
    def _verify_connection(self) -> None:
        """
        Verify connection to the ChromaDB server.
        
        Raises:
            ConnectionError: If unable to connect to the server
        """
        try:
            self.heartbeat()
            logger.debug(f"Connected to ChromaDB at {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    # ========== Tenant Operations ==========

    
    def create_tenant(self, name: str) -> Dict[str, Any]:
        """
        Create a new tenant.
        
        Args:
            name: Name of the tenant to create
            
        Returns:
            Created tenant object
        """
        return self.post(ENDPOINT_TENANTS, API_V2, json_data={FIELD_NAME: name})
    
    def get_tenant(self, name: str) -> Dict[str, Any]:
        """
        Get information about a tenant.
        
        Args:
            name: Name of the tenant
            
        Returns:
            Tenant object
        """
        return self.get(f"{ENDPOINT_TENANTS}/{name}", API_V2)
    
    # ========== Database Operations ==========
    
    def list_databases(self, tenant: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all databases for a tenant.
        
        Args:
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            List of database objects
        """
        tenant = tenant or self.tenant
        return self.get(f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}", API_V2)
    
    def create_database(self, name: str, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new database.
        
        Args:
            name: Name of the database to create
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Created database object
        """
        tenant = tenant or self.tenant
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}", 
            API_V2,
            json_data={FIELD_NAME: name}
        )
    
    def get_database(self, name: str, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a database.
        
        Args:
            name: Name of the database
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Database object
        """
        tenant = tenant or self.tenant
        return self.get(f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{name}", API_V2)
    
    def delete_database(self, name: str, tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a database.
        
        Args:
            name: Name of the database to delete
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self.tenant
        return self.delete(f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{name}", API_V2)
    
    def count_collections(self, database: Optional[str] = None, tenant: Optional[str] = None) -> int:
        """
        Count collections in a database.
        
        Args:
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Number of collections in the database
        """
        tenant = tenant or self.tenant
        database = database or self.database
        response = self.get(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/collections_count", 
            API_V2
        )
        return response
    
    # ========== Collection Operations ==========
    
    def list_collections(
        self, 
        database: Optional[str] = None, 
        tenant: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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
        tenant = tenant or self.tenant
        database = database or self.database
        
        params = {}
        if limit is not None:
            params[PARAM_LIMIT] = limit
        if offset is not None:
            params[PARAM_OFFSET] = offset
            
        return self.get(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}", 
            API_V2,
            params=params
        )
    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding_function: Optional[Dict[str, Any]] = None,
        dimension: Optional[int] = None,
        get_or_create: bool = False,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new collection.
        
        Args:
            name: Name of the collection to create
            metadata: Optional metadata for the collection
            embedding_function: Optional embedding function configuration
            dimension: Vector dimension (default is 768)
            get_or_create: If True, return existing collection if it exists
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Created collection object
        """
        tenant = tenant or self.tenant
        database = database or self.database
        
        # Prepare the base request data
        json_data = {
            FIELD_NAME: name,
            "get_or_create": get_or_create
        }
        
        # Add metadata if provided
        if metadata is not None:
            json_data[FIELD_METADATA] = metadata
        
        # Prepare configuration if needed
        configuration = {}
        
        # Add embedding function configuration if provided
        if embedding_function is not None:
            configuration["embedding_function"] = embedding_function
        
        # Add HNSW configuration with dimension if provided
        if dimension is not None:
            hnsw_config = {"dimension": dimension}
            configuration["hnsw"] = hnsw_config
        
        # Add configuration to request if not empty
        if configuration:
            json_data["configuration"] = configuration
        
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}", 
            API_V2,
            json_data=json_data
        )

    def get_collection(
        self,
        name: str,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            name: Name of the collection
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Collection object
        """
        tenant = tenant or self.tenant
        database = database or self.database
        
        return self.get(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{name}", 
            API_V2
        )
    
    def delete_collection(
        self,
        name: str,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a collection.
        
        Args:
            name: Name of the collection to delete
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self.tenant
        database = database or self.database
        
        return self.delete(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{name}", 
            API_V2
        )
    
    def update_collection(
        self,
        collection_id: str,
        new_name: Optional[str] = None,
        new_metadata: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
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
        tenant = tenant or self.tenant
        database = database or self.database
        
        json_data = {}
        if new_name is not None:
            json_data["new_name"] = new_name
        if new_metadata is not None:
            json_data["new_metadata"] = new_metadata
            
        return self.put(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}", 
            API_V2,
            json_data=json_data
        )
    
    def count_items(
        self,
        collection_id: str,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> int:
        """
        Count items in a collection.
        
        Args:
            collection_id: ID of the collection
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Number of items in the collection
        """
        tenant = tenant or self.tenant
        database = database or self.database
        
        response = self.get(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_COUNT}", 
            API_V2
        )
        return response
    
    # ========== Collection Data Operations ==========
    
    def add_items(
        self,
        collection_id: str,
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add items to a collection.
        
        Args:
            collection_id: ID of the collection
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            documents: Optional list of document strings
            ids: Optional list of IDs (UUIDs will be generated if not provided)
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self.tenant
        database = database or self.database
        
        json_data = {
            FIELD_EMBEDDINGS: embeddings
        }
        
        if metadatas is not None:
            json_data[FIELD_METADATAS] = metadatas
            
        if documents is not None:
            json_data[FIELD_DOCUMENTS] = documents
            
        if ids is not None:
            json_data[FIELD_IDS] = ids
            
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_ADD}", 
            API_V2,
            json_data=json_data
        )
    
    def update_items(
        self,
        collection_id: str,
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
        ids: List[str] = [],
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update items in a collection.
        
        Args:
            collection_id: ID of the collection
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            documents: Optional list of document strings
            ids: List of IDs to update
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self.tenant
        database = database or self.database
        
        json_data = {
            FIELD_EMBEDDINGS: embeddings,
            FIELD_IDS: ids
        }
        
        if metadatas is not None:
            json_data[FIELD_METADATAS] = metadatas
            
        if documents is not None:
            json_data[FIELD_DOCUMENTS] = documents
            
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_UPDATE}", 
            API_V2,
            json_data=json_data
        )
    
    def upsert_items(
        self,
        collection_id: str,
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
        ids: List[str] = [],
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upsert items in a collection (update if exists, add if not).
        
        Args:
            collection_id: ID of the collection
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            documents: Optional list of document strings
            ids: List of IDs to upsert
            database: Database name (defaults to client's default database)
            tenant: Tenant name (defaults to client's default tenant)
            
        Returns:
            Response data
        """
        tenant = tenant or self.tenant
        database = database or self.database
        
        json_data = {
            FIELD_EMBEDDINGS: embeddings,
            FIELD_IDS: ids
        }
        
        if metadatas is not None:
            json_data[FIELD_METADATAS] = metadatas
            
        if documents is not None:
            json_data[FIELD_DOCUMENTS] = documents
            
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_UPSERT}", 
            API_V2,
            json_data=json_data
        )
    
    def get_items(
        self,
        collection_id: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include: Optional[List[str]] = None,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
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
        tenant = tenant or self.tenant
        database = database or self.database
        
        json_data = {}
        
        if ids is not None:
            json_data[FIELD_IDS] = ids
            
        if where is not None:
            json_data[FIELD_WHERE] = where
            
        if where_document is not None:
            json_data[FIELD_WHERE_DOCUMENT] = where_document
            
        if limit is not None:
            json_data["limit"] = limit
            
        if offset is not None:
            json_data["offset"] = offset
            
        if include is not None:
            json_data["include"] = include
            
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_GET}", 
            API_V2,
            json_data=json_data
        )
    
    def delete_items(
        self,
        collection_id: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
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
        tenant = tenant or self.tenant
        database = database or self.database
        
        json_data = {}
        
        if ids is not None:
            json_data[FIELD_IDS] = ids
            
        if where is not None:
            json_data[FIELD_WHERE] = where
            
        if where_document is not None:
            json_data[FIELD_WHERE_DOCUMENT] = where_document
            
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_DELETE}", 
            API_V2,
            json_data=json_data
        )
    
    def query(
        self,
        collection_id: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
        database: Optional[str] = None,
        tenant: Optional[str] = None
    ) -> Dict[str, Any]:
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
        tenant = tenant or self.tenant
        database = database or self.database
        
        json_data = {
            "query_embeddings": query_embeddings,
            FIELD_N_RESULTS: n_results
        }
        
        if where is not None:
            json_data[FIELD_WHERE] = where
            
        if where_document is not None:
            json_data[FIELD_WHERE_DOCUMENT] = where_document
            
        if include is not None:
            json_data["include"] = include
            
        return self.post(
            f"{ENDPOINT_TENANTS}/{tenant}/{ENDPOINT_DATABASES}/{database}/{ENDPOINT_COLLECTIONS}/{collection_id}/{ENDPOINT_QUERY}", 
            API_V2,
            json_data=json_data
        )