"""
Common test fixtures and configurations for ChromaLens test suite.
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock

# Conditionally import the client - allows tests to run even if package is not installed
try:
    from chromalens.client.client import ChromaLensClient
except ImportError:
    ChromaLensClient = MagicMock()

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def mock_client():
    """Return a mocked client that doesn't make actual API calls"""
    client = MagicMock(spec=ChromaLensClient)
    
    # Setup common mock return values
    client.heartbeat.return_value = 123456789
    client.version.return_value = "0.1.0"
    
    # Mock collections
    mock_collections = [
        {"id": "col1", "name": "test_collection", "dimension": 128, "metadata": {"description": "Test collection"}},
        {"id": "col2", "name": "embeddings", "dimension": 768, "metadata": {"description": "Embeddings collection"}}
    ]
    client.list_collections.return_value = mock_collections
    
    # Mock tenants
    mock_tenants = [
        {"id": "ten1", "name": "default_tenant"},
        {"id": "ten2", "name": "test_tenant"}
    ]
    client.list_tenants.return_value = mock_tenants
    
    # Mock databases
    mock_databases = [
        {"id": "db1", "name": "default_database", "tenant": "default_tenant"},
        {"id": "db2", "name": "test_database", "tenant": "test_tenant"}
    ]
    client.list_databases.return_value = mock_databases
    
    return client

@pytest.fixture
def real_client():
    """
    Return a real client connected to a test ChromaDB instance.
    
    This fixture will be skipped if no test ChromaDB instance is available.
    Set CHROMADB_TEST_HOST and CHROMADB_TEST_PORT environment variables to
    point to your test instance.
    """
    # Check if we should attempt real connection tests
    test_host = os.environ.get("CHROMADB_TEST_HOST")
    test_port = os.environ.get("CHROMADB_TEST_PORT")
    
    if not test_host or not test_port:
        pytest.skip("No CHROMADB_TEST_HOST or CHROMADB_TEST_PORT environment variables set")
    
    try:
        client = ChromaLensClient(
            host=test_host,
            port=int(test_port),
            tenant="test_tenant",
            database="test_database"
        )
        
        # Test connection
        client.heartbeat()
        
        # Setup test environment
        tenants = client.list_tenants()
        if not any(t["name"] == "test_tenant" for t in tenants):
            client.create_tenant("test_tenant")
        
        databases = client.list_databases(tenant="test_tenant")
        if not any(d["name"] == "test_database" for d in databases):
            client.create_database("test_database", tenant="test_tenant")
        
        yield client
        
        # Cleanup any test collections
        collections = client.list_collections(tenant="test_tenant", database="test_database")
        for coll in collections:
            if coll["name"].startswith("test_"):
                try:
                    client.delete_collection(coll["name"])
                except Exception:
                    pass
        
    except Exception as e:
        pytest.skip(f"Test ChromaDB instance not available: {e}")

@pytest.fixture
def sample_embeddings():
    """Return sample embeddings for testing"""
    import numpy as np
    # Create 10 sample embeddings of dimension 128
    return np.random.rand(10, 128).tolist()

@pytest.fixture
def sample_documents():
    """Return sample documents for testing"""
    return [
        "This is the first test document",
        "Another document for testing vector search",
        "ChromaDB is a vector database",
        "Embeddings are numerical representations of data",
        "Vector search enables semantic similarity queries",
        "LLMs can generate vector embeddings for text",
        "ChromaLens is a client for ChromaDB",
        "Vector databases store and query high-dimensional vectors",
        "Semantic search is powerful for unstructured data",
        "Cosine similarity measures the angle between vectors"
    ]

@pytest.fixture
def sample_metadata():
    """Return sample metadata for testing"""
    return [
        {"source": "test", "category": "documentation", "length": 31},
        {"source": "test", "category": "documentation", "length": 37},
        {"source": "test", "category": "definition", "length": 29},
        {"source": "test", "category": "definition", "length": 50},
        {"source": "test", "category": "description", "length": 46},
        {"source": "test", "category": "technology", "length": 43},
        {"source": "test", "category": "product", "length": 34},
        {"source": "test", "category": "definition", "length": 53},
        {"source": "test", "category": "technology", "length": 46},
        {"source": "test", "category": "technical", "length": 47}
    ]

# UI test fixtures
@pytest.fixture
def mock_streamlit():
    """
    Mock streamlit module for UI testing
    
    This allows testing UI components without actually rendering them
    """
    with pytest.MonkeyPatch.context() as mp:
        mock_st = MagicMock()
        mock_st.session_state = {}
        mp.setattr("streamlit.session_state", mock_st.session_state)
        yield mock_st