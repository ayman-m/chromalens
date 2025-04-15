"""
Unit tests for the ChromaLensClient class.
"""

import pytest
from unittest.mock import patch, MagicMock, call
import requests
import json

# Import client and exceptions
from chromalens.client.client import ChromaLensClient
from chromalens.exceptions import ClientError, ConnectionError, ConfigurationError
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
)


class TestChromaLensClient:
    """Test suite for ChromaLensClient class"""

    def test_initialization_default_params(self):
        """Test client initialization with default parameters"""
        with patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection') as mock_verify:
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'default-host',
                'port': 9000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Create client
            client = ChromaLensClient()
            
            # Verify settings were used
            assert client.host == 'default-host'
            assert client.port == 9000
            assert client.tenant == 'default_tenant'
            assert client.database == 'default_database'
            assert client.ssl is False
            assert client.base_url == 'http://default-host:9000'
            
            # Verify connection was tested
            mock_verify.assert_called_once()

    def test_initialization_custom_params(self):
        """Test client initialization with custom parameters"""
        with patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection') as mock_verify:
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'default-host',
                'port': 9000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Create client with custom params
            client = ChromaLensClient(
                host='custom-host',
                port=8080,
                tenant='custom_tenant',
                database='custom_db',
                ssl=True,
                api_key='test-api-key',
                timeout=30,
                verify_ssl=False,
            )
            
            # Verify custom params were used
            assert client.host == 'custom-host'
            assert client.port == 8080
            assert client.tenant == 'custom_tenant'
            assert client.database == 'custom_db'
            assert client.ssl is True
            assert client.base_url == 'https://custom-host:8080'
            assert client.timeout == 30
            assert client.headers.get('Authorization') == 'Bearer test-api-key'
            
            # Verify connection was tested
            mock_verify.assert_called_once()

    def test_verify_connection_success(self):
        """Test successful connection verification"""
        with patch.object(ChromaLensClient, 'heartbeat') as mock_heartbeat, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch('chromalens.client.client.logger') as mock_logger:
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock successful heartbeat
            mock_heartbeat.return_value = 123456789
            
            # Create client
            client = ChromaLensClient()
            
            # Verify logger was called
            mock_logger.debug.assert_called_once_with(
                f"Connected to ChromaDB at {client.base_url}"
            )

    def test_verify_connection_failure(self):
        """Test failed connection verification"""
        with patch.object(ChromaLensClient, 'heartbeat') as mock_heartbeat, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch('chromalens.client.client.logger') as mock_logger:
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock failed heartbeat
            mock_heartbeat.side_effect = ConnectionError("Failed to connect")
            
            # Verify exception is raised
            with pytest.raises(ConnectionError, match="Failed to connect"):
                client = ChromaLensClient()
            
            # Verify logger was called
            mock_logger.error.assert_called_once()

    #
    # Tenant Operations Tests
    #
    
    def test_list_tenants(self):
        """Test list_tenants method"""
        with patch.object(ChromaLensClient, 'get') as mock_get, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_tenants = [
                {"id": "ten1", "name": "default_tenant"},
                {"id": "ten2", "name": "test_tenant"}
            ]
            mock_get.return_value = mock_tenants
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.list_tenants()
            
            # Verify results
            assert result == mock_tenants
            mock_get.assert_called_once_with(ENDPOINT_TENANTS, API_V2)

    def test_create_tenant(self):
        """Test create_tenant method"""
        with patch.object(ChromaLensClient, 'post') as mock_post, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_tenant = {"id": "new_ten", "name": "new_tenant"}
            mock_post.return_value = mock_tenant
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.create_tenant("new_tenant")
            
            # Verify results
            assert result == mock_tenant
            mock_post.assert_called_once_with(
                ENDPOINT_TENANTS, 
                API_V2, 
                json_data={"name": "new_tenant"}
            )

    def test_get_tenant(self):
        """Test get_tenant method"""
        with patch.object(ChromaLensClient, 'get') as mock_get, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_tenant = {"id": "ten1", "name": "test_tenant"}
            mock_get.return_value = mock_tenant
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.get_tenant("test_tenant")
            
            # Verify results
            assert result == mock_tenant
            mock_get.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/test_tenant", 
                API_V2
            )

    #
    # Database Operations Tests
    #
    
    def test_list_databases(self):
        """Test list_databases method"""
        with patch.object(ChromaLensClient, 'get') as mock_get, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_databases = [
                {"id": "db1", "name": "default_database", "tenant": "default_tenant"},
                {"id": "db2", "name": "test_database", "tenant": "default_tenant"}
            ]
            mock_get.return_value = mock_databases
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.list_databases()
            
            # Verify results
            assert result == mock_databases
            mock_get.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}", 
                API_V2
            )
            
            # Test with custom tenant
            mock_get.reset_mock()
            result = client.list_databases(tenant="custom_tenant")
            mock_get.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/custom_tenant/{ENDPOINT_DATABASES}", 
                API_V2
            )

    def test_create_database(self):
        """Test create_database method"""
        with patch.object(ChromaLensClient, 'post') as mock_post, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_database = {"id": "new_db", "name": "new_database", "tenant": "default_tenant"}
            mock_post.return_value = mock_database
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.create_database("new_database")
            
            # Verify results
            assert result == mock_database
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}", 
                API_V2, 
                json_data={"name": "new_database"}
            )
            
            # Test with custom tenant
            mock_post.reset_mock()
            mock_post.return_value = {"id": "new_db", "name": "new_database", "tenant": "custom_tenant"}
            result = client.create_database("new_database", tenant="custom_tenant")
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/custom_tenant/{ENDPOINT_DATABASES}", 
                API_V2, 
                json_data={"name": "new_database"}
            )

    def test_delete_database(self):
        """Test delete_database method"""
        with patch.object(ChromaLensClient, 'delete') as mock_delete, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_delete.return_value = {"success": True}
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.delete_database("test_database")
            
            # Verify results
            assert result == {"success": True}
            mock_delete.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}/test_database", 
                API_V2
            )
            
            # Test with custom tenant
            mock_delete.reset_mock()
            result = client.delete_database("test_database", tenant="custom_tenant")
            mock_delete.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/custom_tenant/{ENDPOINT_DATABASES}/test_database", 
                API_V2
            )

    #
    # Collection Operations Tests
    #
    
    def test_list_collections(self):
        """Test list_collections method"""
        with patch.object(ChromaLensClient, 'get') as mock_get, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_collections = [
                {"id": "col1", "name": "test_collection", "dimension": 128},
                {"id": "col2", "name": "embeddings", "dimension": 768}
            ]
            mock_get.return_value = mock_collections
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.list_collections()
            
            # Verify results
            assert result == mock_collections
            mock_get.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}/default_database/{ENDPOINT_COLLECTIONS}", 
                API_V2,
                params={}
            )
            
            # Test with custom params
            mock_get.reset_mock()
            result = client.list_collections(
                database="custom_db", 
                tenant="custom_tenant",
                limit=10,
                offset=5
            )
            mock_get.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/custom_tenant/{ENDPOINT_DATABASES}/custom_db/{ENDPOINT_COLLECTIONS}", 
                API_V2,
                params={"limit": 10, "offset": 5}
            )

    def test_create_collection(self):
        """Test create_collection method"""
        with patch.object(ChromaLensClient, 'post') as mock_post, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_collection = {
                "id": "new_col", 
                "name": "new_collection", 
                "dimension": 128,
                "metadata": {"description": "Test collection"}
            }
            mock_post.return_value = mock_collection
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.create_collection(
                name="new_collection",
                metadata={"description": "Test collection"},
                dimension=128
            )
            
            # Verify results
            assert result == mock_collection
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}/default_database/{ENDPOINT_COLLECTIONS}", 
                API_V2, 
                json_data={
                    "name": "new_collection",
                    "get_or_create": False,
                    "metadata": {"description": "Test collection"},
                    "dimension": 128
                }
            )
            
            # Test with custom params
            mock_post.reset_mock()
            result = client.create_collection(
                name="new_collection",
                get_or_create=True,
                database="custom_db",
                tenant="custom_tenant"
            )
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/custom_tenant/{ENDPOINT_DATABASES}/custom_db/{ENDPOINT_COLLECTIONS}", 
                API_V2, 
                json_data={
                    "name": "new_collection",
                    "get_or_create": True
                }
            )

    def test_delete_collection(self):
        """Test delete_collection method"""
        with patch.object(ChromaLensClient, 'delete') as mock_delete, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Mock response
            mock_delete.return_value = {"success": True}
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.delete_collection("test_collection")
            
            # Verify results
            assert result == {"success": True}
            mock_delete.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}/default_database/{ENDPOINT_COLLECTIONS}/test_collection", 
                API_V2
            )
            
            # Test with custom params
            mock_delete.reset_mock()
            result = client.delete_collection(
                "test_collection",
                database="custom_db",
                tenant="custom_tenant"
            )
            mock_delete.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/custom_tenant/{ENDPOINT_DATABASES}/custom_db/{ENDPOINT_COLLECTIONS}/test_collection", 
                API_V2
            )

    #
    # Collection Data Operations Tests
    #
    
    def test_add(self):
        """Test add method"""
        with patch.object(ChromaLensClient, 'post') as mock_post, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Test data
            embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            metadatas = [{"source": "test1"}, {"source": "test2"}]
            documents = ["Document 1", "Document 2"]
            ids = ["id1", "id2"]
            
            # Mock response
            mock_post.return_value = {"success": True}
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.add(
                collection_id="col1",
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
                ids=ids
            )
            
            # Verify results
            assert result == {"success": True}
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}/default_database/{ENDPOINT_COLLECTIONS}/col1/{ENDPOINT_ADD}", 
                API_V2, 
                json_data={
                    "embeddings": embeddings,
                    "metadatas": metadatas,
                    "documents": documents,
                    "ids": ids
                }
            )
            
            # Test with custom tenant/database
            mock_post.reset_mock()
            result = client.add(
                collection_id="col1",
                embeddings=embeddings,
                database="custom_db",
                tenant="custom_tenant"
            )
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/custom_tenant/{ENDPOINT_DATABASES}/custom_db/{ENDPOINT_COLLECTIONS}/col1/{ENDPOINT_ADD}", 
                API_V2, 
                json_data={
                    "embeddings": embeddings
                }
            )

    def test_query(self):
        """Test query method"""
        with patch.object(ChromaLensClient, 'post') as mock_post, \
             patch('chromalens.client.client.get_settings') as mock_get_settings, \
             patch.object(ChromaLensClient, '_verify_connection'):
            
            # Mock settings
            mock_get_settings.return_value = {
                'host': 'test-host',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'timeout': 10,
                'verify_ssl': True,
            }
            
            # Test data
            query_embeddings = [[0.1, 0.2, 0.3]]
            where = {"metadata_field": "value"}
            include = ["documents", "metadatas", "distances"]
            
            # Mock response
            mock_response = {
                "ids": [["id1", "id2", "id3"]],
                "documents": [["doc1", "doc2", "doc3"]],
                "distances": [[0.1, 0.2, 0.3]]
            }
            mock_post.return_value = mock_response
            
            # Create client and call method
            client = ChromaLensClient()
            result = client.query(
                collection_id="col1",
                query_embeddings=query_embeddings,
                n_results=3,
                where=where,
                include=include
            )
            
            # Verify results
            assert result == mock_response
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}/default_database/{ENDPOINT_COLLECTIONS}/col1/{ENDPOINT_QUERY}", 
                API_V2, 
                json_data={
                    "query_embeddings": query_embeddings,
                    "n_results": 3,
                    "where": where,
                    "include": include
                }
            )
            
            # Test with minimal parameters
            mock_post.reset_mock()
            result = client.query(
                collection_id="col1",
                query_embeddings=query_embeddings
            )
            mock_post.assert_called_once_with(
                f"{ENDPOINT_TENANTS}/default_tenant/{ENDPOINT_DATABASES}/default_database/{ENDPOINT_COLLECTIONS}/col1/{ENDPOINT_QUERY}", 
                API_V2, 
                json_data={
                    "query_embeddings": query_embeddings,
                    "n_results": 10
                }
            )