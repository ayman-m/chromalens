"""
Integration tests for ChromaLensClient against a real ChromaDB server.

This test file is intended to be run against a real ChromaDB instance to verify
that the client works correctly in real-world scenarios.

To run these tests:
1. Ensure you have a ChromaDB server running
2. Update the connection details below
3. Run with: pytest -xvs tests/integration/test_real_client.py
"""

import pytest
import uuid
import time
import logging

from chromalens.client.client import ChromaLensClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure these variables with your ChromaDB connection details
CHROMA_HOST = "127.0.0.1"  # Replace with your ChromaDB host
CHROMA_PORT = 8008         # Replace with your ChromaDB port
USE_SSL = False            # Set to True if your ChromaDB server uses HTTPS
API_KEY = None             # Add your API key if required

# Test data
SAMPLE_DOCUMENTS = [
    "This is the first test document",
    "Another document for testing vector search",
    "ChromaDB is a vector database",
    "Embeddings are numerical representations of data",
    "Vector search enables semantic similarity queries"
]

SAMPLE_METADATA = [
    {"source": "test", "category": "example", "id": 1},
    {"source": "test", "category": "example", "id": 2},
    {"source": "test", "category": "definition", "id": 3},
    {"source": "test", "category": "definition", "id": 4},
    {"source": "test", "category": "description", "id": 5}
]

class TestChromaLensClient:
    """Integration tests for ChromaLensClient with a real ChromaDB server"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create a real ChromaLensClient connected to a ChromaDB server"""
        try:
            client = ChromaLensClient(
                host=CHROMA_HOST,
                port=CHROMA_PORT,
                ssl=USE_SSL,
                api_key=API_KEY
            )
            # Test connection
            heartbeat = client.heartbeat()
            logger.info(f"Connected to ChromaDB server: {CHROMA_HOST}:{CHROMA_PORT}")
            logger.info(f"Server heartbeat: {heartbeat}")
            
            return client
        except Exception as e:
            pytest.skip(f"Could not connect to ChromaDB server: {e}")
    
    @pytest.fixture(scope="class")
    def test_tenant(self, client):
        """Create a temporary test tenant"""
        tenant_name = f"test_tenant_{uuid.uuid4().hex[:8]}"
        logger.info(f"Creating test tenant: {tenant_name}")
        
        try:
            client.create_tenant(tenant_name)
            logger.info(f"Test tenant created: {tenant_name}")
            yield tenant_name
            
            # Cleanup
            logger.info(f"Cleaning up test tenant: {tenant_name}")
            # Note: ChromaDB might not support tenant deletion via API
            # This is left here in case that functionality is added
        except Exception as e:
            logger.error(f"Error creating test tenant: {e}")
            pytest.skip(f"Could not create test tenant: {e}")
    
    @pytest.fixture(scope="class")
    def test_database(self, client, test_tenant):
        """Create a temporary test database"""
        database_name = f"test_db_{uuid.uuid4().hex[:8]}"
        logger.info(f"Creating test database: {database_name} in tenant: {test_tenant}")
        
        try:
            client.create_database(database_name, tenant=test_tenant)
            logger.info(f"Test database created: {database_name}")
            yield database_name
            
            # Cleanup
            logger.info(f"Cleaning up test database: {database_name}")
            try:
                client.delete_database(database_name, tenant=test_tenant)
                logger.info(f"Test database deleted: {database_name}")
            except Exception as e:
                logger.error(f"Error deleting test database: {e}")
        except Exception as e:
            logger.error(f"Error creating test database: {e}")
            pytest.skip(f"Could not create test database: {e}")
    
    @pytest.fixture(scope="function")
    def test_collection(self, client, test_tenant, test_database):
        """Create a temporary test collection for each test"""
        collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
        logger.info(f"Creating test collection: {collection_name}")
        
        try:
            result = client.create_collection(
                name=collection_name,
                metadata={"description": "Test collection for integration tests"},
                dimension=384,  # A common embedding dimension
                tenant=test_tenant,
                database=test_database
            )
            logger.info(f"Test collection created: {collection_name} (ID: {result.get('id')})")
            yield collection_name
            
            # Cleanup
            logger.info(f"Cleaning up test collection: {collection_name}")
            try:
                client.delete_collection(collection_name, tenant=test_tenant, database=test_database)
                logger.info(f"Test collection deleted: {collection_name}")
            except Exception as e:
                logger.error(f"Error deleting test collection: {e}")
        except Exception as e:
            logger.error(f"Error creating test collection: {e}")
            pytest.skip(f"Could not create test collection: {e}")
    
    def test_heartbeat_and_version(self, client):
        """Test basic server connection"""
        # Test heartbeat
        heartbeat = client.heartbeat()
        assert heartbeat is not None
        logger.info(f"Server heartbeat: {heartbeat}")
        
        # Test version
        version = client.version()
        assert version is not None
        logger.info(f"Server version: {version}")
    
    def test_tenant_operations(self, client, test_tenant):
        """Test tenant operations"""
        # Get tenant info
        tenant_info = client.get_tenant(test_tenant)
        assert tenant_info.get('name') == test_tenant
        logger.info(f"Retrieved tenant info: {tenant_info}")
    
    def test_database_operations(self, client, test_tenant):
        """Test database operations"""
        # List initial databases
        initial_databases = client.list_databases(tenant=test_tenant)
        assert isinstance(initial_databases, list)
        logger.info(f"Initially found {len(initial_databases)} databases in tenant {test_tenant}")
        
        # Create a new test database
        new_db_name = f"test_db_created_{uuid.uuid4().hex[:8]}"
        logger.info(f"Creating new test database: {new_db_name}")
        
        try:
            # Create database - API returns 200 OK but no content
            create_response = client.create_database(new_db_name, tenant=test_tenant)
            # For APIs that return nothing or just a success status, this might be None, {} or True
            logger.info(f"Database creation response: {create_response}")
            
            # Give the server a moment to process (if needed)
            time.sleep(0.5)
            
            # List databases again to confirm addition
            updated_databases = client.list_databases(tenant=test_tenant)
            
            # Verify our new database exists in the list
            updated_db_names = [d.get('name') for d in updated_databases]
            assert new_db_name in updated_db_names, f"Newly created database {new_db_name} not found in listing"
            logger.info(f"Confirmed new database exists in listing: {new_db_name}")
            
            # Get database info (if supported by the API)
            try:
                database_info = client.get_database(new_db_name, tenant=test_tenant)
                assert database_info is not None, "get_database returned None"
                assert database_info.get('name') == new_db_name, "Database name in response doesn't match"
                logger.info(f"Retrieved database info: {database_info}")
            except Exception as e:
                logger.warning(f"Could not get database info (this might be expected if the API doesn't support it): {e}")
            
            # Now delete the database
            logger.info(f"Deleting test database: {new_db_name}")
            delete_response = client.delete_database(new_db_name, tenant=test_tenant)
            # For APIs that return nothing or just a success status
            logger.info(f"Database deletion response: {delete_response}")
            
            # Give the server a moment to process (if needed)
            time.sleep(0.5)
            
            # Verify deletion
            final_databases = client.list_databases(tenant=test_tenant)
            final_db_names = [d.get('name') for d in final_databases]
            assert new_db_name not in final_db_names, f"Database {new_db_name} still exists after deletion"
            logger.info(f"Confirmed database was deleted: {new_db_name}")
                    # Count collections in the default database
            try:
                default_db = client.database or "default_database"
                collection_count = client.count_collections(database=default_db, tenant=test_tenant)
                logger.info(f"Number of collections in '{default_db}': {collection_count}")
                
                # Verify the count is a number
                assert isinstance(collection_count, (int, float)), "Collection count should be a number"
                
                # If there are collections, try listing them
                if collection_count > 0:
                    collections = client.list_collections(database=default_db, tenant=test_tenant)
                    logger.info(f"Found {len(collections)} collections in '{default_db}'")
                    # Verify the list length matches the count
                    assert len(collections) == collection_count, "Collection count doesn't match list length"
                
            except Exception as e:
                logger.warning(f"Error counting collections: {e}")
        except Exception as e:
            logger.error(f"Error in database operations test: {e}")
            # Try to clean up if something failed
            try:
                client.delete_database(new_db_name, tenant=test_tenant)
            except:
                pass
            raise

    def test_collection_operations(self, client, test_tenant, test_database, test_collection):
        """Test collection operations"""
        # List collections
        collections = client.list_collections(tenant=test_tenant, database=test_database)
        assert isinstance(collections, list)
        logger.info(f"Found {len(collections)} collections in database {test_database}")
        
        # Verify our test collection exists
        collection_names = [c.get('name') for c in collections]
        assert test_collection in collection_names
        logger.info(f"Confirmed test collection exists: {test_collection}")
        
        # Get collection info
        collection_info = client.get_collection(test_collection, tenant=test_tenant, database=test_database)
        assert collection_info.get('name') == test_collection
        assert collection_info.get('metadata', {}).get('description') == "Test collection for integration tests"
        logger.info(f"Retrieved collection info: {collection_info}")
        
        # Get collection by ID
        collection_id = collection_info.get('id')
        if collection_id:
            try:
                collection_by_id = client.get_collection(collection_id, tenant=test_tenant, database=test_database)
                assert collection_by_id.get('id') == collection_id
                logger.info(f"Retrieved collection by ID: {collection_id}")
            except Exception as e:
                logger.warning(f"Could not get collection by ID: {e}")
    
    def test_add_and_query_documents(self, client, test_tenant, test_database, test_collection):
        """Test adding and querying documents"""
        # Generate test data
        documents = SAMPLE_DOCUMENTS
        metadatas = SAMPLE_METADATA
        ids = [f"doc_{i+1}" for i in range(len(documents))]
        
        # Create some sample embeddings (random for testing)
        # In a real scenario, you would use proper embedding models
        import numpy as np
        np.random.seed(42)  # For reproducibility
        dimension = 384
        embeddings = [np.random.rand(dimension).tolist() for _ in range(len(documents))]
        
        # Add documents
        logger.info(f"Adding {len(documents)} documents to collection {test_collection}")
        result = client.add(
            collection_id=test_collection,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            tenant=test_tenant,
            database=test_database
        )
        logger.info(f"Add result: {result}")
        
        # Wait for documents to be indexed
        time.sleep(1)
        
        # Get all documents
        logger.info(f"Retrieving documents from collection {test_collection}")
        items = client.get(
            collection_id=test_collection,
            tenant=test_tenant,
            database=test_database,
            include=["documents", "metadatas", "embeddings"]
        )
        
        # Verify documents were added correctly
        assert "ids" in items
        assert len(items["ids"]) == len(ids)
        assert set(items["ids"]) == set(ids)
        assert "documents" in items
        assert len(items["documents"]) == len(documents)
        logger.info("Successfully retrieved all documents")
        
        # Query for similar documents
        logger.info("Testing vector query")
        query_results = client.query(
            collection_id=test_collection,
            query_embeddings=[embeddings[0]],  # Query with the first embedding
            n_results=3,
            tenant=test_tenant,
            database=test_database,
            include=["documents", "metadatas", "distances"]
        )
        
        # Verify query results
        assert "ids" in query_results
        assert len(query_results["ids"]) == 1  # One query
        assert len(query_results["ids"][0]) <= 3  # Up to 3 results
        assert "documents" in query_results
        assert "distances" in query_results
        logger.info(f"Query returned {len(query_results['ids'][0])} results")
        
        # Test filter query
        logger.info("Testing filtered query")
        filtered_results = client.query(
            collection_id=test_collection,
            query_embeddings=[embeddings[0]],
            n_results=3,
            where={"category": "definition"},
            tenant=test_tenant,
            database=test_database,
            include=["documents", "metadatas", "distances"]
        )
        
        # Verify filtered results
        assert "ids" in filtered_results
        if filtered_results["ids"][0]:
            logger.info(f"Filtered query returned {len(filtered_results['ids'][0])} results")
            # Verify filter was applied
            for i, doc_id in enumerate(filtered_results["ids"][0]):
                metadata = filtered_results["metadatas"][0][i]
                assert metadata["category"] == "definition"
        else:
            logger.info("Filtered query returned no results")
    
    def test_update_and_delete(self, client, test_tenant, test_database, test_collection):
        """Test updating and deleting documents"""
        # Add a document
        document = "This is a test document to update"
        metadata = {"source": "test", "status": "new"}
        doc_id = "update_test_doc"
        
        # Create a sample embedding (random for testing)
        import numpy as np
        np.random.seed(42)
        dimension = 384
        embedding = np.random.rand(dimension).tolist()
        
        # Add document
        logger.info(f"Adding document for update test")
        client.add(
            collection_id=test_collection,
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
            ids=[doc_id],
            tenant=test_tenant,
            database=test_database
        )
        
        # Wait for document to be indexed
        time.sleep(1)
        
        # Update document
        updated_document = "This is an updated test document"
        updated_metadata = {"source": "test", "status": "updated"}
        updated_embedding = np.random.rand(dimension).tolist()
        
        logger.info(f"Updating document")
        client.update(
            collection_id=test_collection,
            embeddings=[updated_embedding],
            documents=[updated_document],
            metadatas=[updated_metadata],
            ids=[doc_id],
            tenant=test_tenant,
            database=test_database
        )
        
        # Wait for update to be processed
        time.sleep(1)
        
        # Get updated document
        updated_item = client.get(
            collection_id=test_collection,
            ids=[doc_id],
            tenant=test_tenant,
            database=test_database,
            include=["documents", "metadatas"]
        )
        
        # Verify update
        assert updated_item["documents"][0] == updated_document
        assert updated_item["metadatas"][0]["status"] == "updated"
        logger.info("Successfully verified document update")
        
        # Delete document
        logger.info("Testing document deletion")
        client.delete(
            collection_id=test_collection,
            ids=[doc_id],
            tenant=test_tenant,
            database=test_database
        )
        
        # Wait for deletion to be processed
        time.sleep(1)
        
        # Verify deletion
        deleted_check = client.get(
            collection_id=test_collection,
            ids=[doc_id],
            tenant=test_tenant,
            database=test_database
        )
        
        assert len(deleted_check["ids"]) == 0, "Document should have been deleted"
        logger.info("Successfully verified document deletion")