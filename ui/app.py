"""
ChromaLens - A powerful user interface for ChromaDB vector database management.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

from chromalens.client.client import ChromaLensClient
from chromalens.utils.formatters import format_json, format_collection_info, format_timestamp

# App title and configuration
st.set_page_config(
    page_title="ChromaLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B7BEC;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .success-box {
        padding: 1rem;
        background-color: #D5F5E3;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2ECC71;
    }
    .info-box {
        padding: 1rem;
        background-color: #D6EAF8;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #3498DB;
    }
    .warning-box {
        padding: 1rem;
        background-color: #FCF3CF;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #F1C40F;
    }
    .error-box {
        padding: 1rem;
        background-color: #F9EBEA;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #E74C3C;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">ChromaLens</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">A powerful interface for ChromaDB vector database management</p>', unsafe_allow_html=True)

# Initialize session state variables
if 'client' not in st.session_state:
    st.session_state.client = None
if 'connection_params' not in st.session_state:
    st.session_state.connection_params = {
        'host': 'localhost',
        'port': 8000,
        'tenant': 'default_tenant',
        'database': 'default_database',
        'ssl': False,
        'api_key': None
    }
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'tenants' not in st.session_state:
    st.session_state.tenants = []
if 'databases' not in st.session_state:
    st.session_state.databases = []
if 'collections' not in st.session_state:
    st.session_state.collections = []
if 'current_collection' not in st.session_state:
    st.session_state.current_collection = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None


# Function to connect to ChromaDB
def connect_to_chroma():
    try:
        st.session_state.client = ChromaLensClient(
            host=st.session_state.connection_params['host'],
            port=st.session_state.connection_params['port'],
            tenant=st.session_state.connection_params['tenant'],
            database=st.session_state.connection_params['database'],
            ssl=st.session_state.connection_params['ssl'],
            api_key=st.session_state.connection_params['api_key'],
        )
        
        # Test connection
        heartbeat = st.session_state.client.heartbeat()
        st.session_state.connected = True
        st.session_state.last_refresh = datetime.now()
        
        # Load tenants, databases, and collections
        refresh_data()
        
        return True, f"Connected successfully! Server heartbeat: {heartbeat}"
    
    except Exception as e:
        st.session_state.connected = False
        return False, f"Connection failed: {str(e)}"


# Function to refresh data from ChromaDB
def refresh_data():
    if not st.session_state.client:
        return False, "No client connection"
    
    try:
        # Get tenants
        st.session_state.tenants = st.session_state.client.list_tenants()
        
        # Get databases for current tenant
        st.session_state.databases = st.session_state.client.list_databases(
            tenant=st.session_state.connection_params['tenant']
        )
        
        # Get collections for current database
        st.session_state.collections = st.session_state.client.list_collections(
            database=st.session_state.connection_params['database'],
            tenant=st.session_state.connection_params['tenant']
        )
        
        st.session_state.last_refresh = datetime.now()
        return True, "Data refreshed successfully"
    
    except Exception as e:
        return False, f"Failed to refresh data: {str(e)}"


# Sidebar for connection management
with st.sidebar:
    st.subheader("Connection Settings")
    
    # Connection form
    with st.form("connection_form"):
        st.session_state.connection_params['host'] = st.text_input(
            "Host", value=st.session_state.connection_params['host']
        )
        st.session_state.connection_params['port'] = st.number_input(
            "Port", value=st.session_state.connection_params['port'],
            min_value=1, max_value=65535
        )
        st.session_state.connection_params['ssl'] = st.checkbox(
            "Use SSL", value=st.session_state.connection_params['ssl']
        )
        st.session_state.connection_params['api_key'] = st.text_input(
            "API Key (if required)", value=st.session_state.connection_params['api_key'] or "",
            type="password"
        )
        
        col1, col2 = st.columns(2)
        connect_button = col1.form_submit_button("Connect")
        disconnect_button = col2.form_submit_button("Disconnect")
    
    if connect_button:
        success, message = connect_to_chroma()
        if success:
            st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
    
    if disconnect_button:
        st.session_state.client = None
        st.session_state.connected = False
        st.markdown('<div class="info-box">Disconnected from server</div>', unsafe_allow_html=True)
    
    # Show connection status
    if st.session_state.connected:
        st.markdown('<div class="success-box">✅ Connected</div>', unsafe_allow_html=True)
        if st.session_state.last_refresh:
            st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        # Tenant and database selection
        if st.session_state.tenants:
            tenant_names = [t.get('name') for t in st.session_state.tenants]
            selected_tenant = st.selectbox(
                "Tenant", options=tenant_names,
                index=tenant_names.index(st.session_state.connection_params['tenant']) 
                if st.session_state.connection_params['tenant'] in tenant_names else 0
            )
            
            if selected_tenant != st.session_state.connection_params['tenant']:
                st.session_state.connection_params['tenant'] = selected_tenant
                # Refresh databases when tenant changes
                refresh_data()
        
        if st.session_state.databases:
            database_names = [d.get('name') for d in st.session_state.databases]
            selected_database = st.selectbox(
                "Database", options=database_names,
                index=database_names.index(st.session_state.connection_params['database'])
                if st.session_state.connection_params['database'] in database_names else 0
            )
            
            if selected_database != st.session_state.connection_params['database']:
                st.session_state.connection_params['database'] = selected_database
                # Refresh collections when database changes
                refresh_data()
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            success, message = refresh_data()
            if success:
                st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="warning-box">❌ Not connected</div>', unsafe_allow_html=True)
    
    # About section
    st.sidebar.markdown("---")
    st.sidebar.subheader("About ChromaLens")
    st.sidebar.markdown(
        "ChromaLens is an open-source tool for managing and visualizing "
        "ChromaDB vector databases. Learn more on [GitHub](https://github.com/yourusername/chromalens)."
    )


# Main content area
if not st.session_state.connected:
    # Show welcome screen when not connected
    st.markdown("## Welcome to ChromaLens! 👋")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(
            """
            ChromaLens is a powerful interface for ChromaDB vector database management.
            
            To get started:
            1. Configure your connection settings in the sidebar
            2. Click "Connect" to connect to your ChromaDB server
            3. Explore and manage your vector database with ease!
            
            ChromaLens allows you to:
            * Manage tenants, databases, and collections
            * Upload and embed documents
            * Visualize vector embeddings
            * Search and query your vector database
            * Monitor and analyze your ChromaDB instance
            """
        )
    
    with col2:
        st.markdown(
            """
            ### Quick Connection:
            
            **Local ChromaDB:**
            * Host: localhost
            * Port: 8000
            * Tenant: default_tenant
            * Database: default_database
            
            **Example Data:**
            """
        )
        
        if st.button("Load Example Data"):
            st.session_state.connection_params = {
                'host': 'localhost',
                'port': 8000,
                'tenant': 'default_tenant',
                'database': 'default_database',
                'ssl': False,
                'api_key': None
            }
            success, message = connect_to_chroma()
            if success:
                st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)

else:
    # Show main interface when connected
    tabs = st.tabs([
        "Dashboard", 
        "Tenants", 
        "Databases", 
        "Collections", 
        "Query", 
        "Analytics"
    ])
    
    # Dashboard Tab
    with tabs[0]:
        st.header("Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tenants", len(st.session_state.tenants))
        
        with col2:
            st.metric("Databases", len(st.session_state.databases))
        
        with col3:
            st.metric("Collections", len(st.session_state.collections))
        
        st.subheader("Server Information")
        try:
            version = st.session_state.client.version()
            st.info(f"ChromaDB Version: {version}")
        except Exception as e:
            st.error(f"Failed to get version: {e}")
        
        st.subheader("Collections")
        if st.session_state.collections:
            collections_df = pd.DataFrame([
                {
                    "Name": c.get("name"),
                    "ID": c.get("id"),
                    "Dimension": c.get("dimension"),
                    "Has Metadata": "Yes" if c.get("metadata") else "No"
                }
                for c in st.session_state.collections
            ])
            
            st.dataframe(collections_df, use_container_width=True)
        else:
            st.info(f"No collections found in database '{st.session_state.connection_params['database']}'")
    
    # Tenants Tab
    with tabs[1]:
        st.header("Tenant Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Existing Tenants")
            
            if st.session_state.tenants:
                tenants_df = pd.DataFrame([
                    {"ID": t.get("id"), "Name": t.get("name")}
                    for t in st.session_state.tenants
                ])
                
                st.dataframe(tenants_df, use_container_width=True)
            else:
                st.info("No tenants found")
        
        with col2:
            st.subheader("Create New Tenant")
            
            with st.form("create_tenant_form"):
                tenant_name = st.text_input("Tenant Name")
                submit_button = st.form_submit_button("Create Tenant")
            
            if submit_button and tenant_name:
                try:
                    response = st.session_state.client.create_tenant(tenant_name)
                    st.success(f"Tenant '{tenant_name}' created successfully!")
                    # Refresh tenants list
                    refresh_data()
                except Exception as e:
                    st.error(f"Failed to create tenant: {e}")
    
    # Databases Tab
    with tabs[2]:
        st.header("Database Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Existing Databases")
            
            if st.session_state.databases:
                databases_df = pd.DataFrame([
                    {
                        "ID": d.get("id"),
                        "Name": d.get("name"),
                        "Tenant": d.get("tenant")
                    }
                    for d in st.session_state.databases
                ])
                
                st.dataframe(databases_df, use_container_width=True)
                
                # Database actions
                selected_db = st.selectbox(
                    "Select Database for Actions",
                    options=[d.get("name") for d in st.session_state.databases]
                )
                
                if selected_db:
                    col1a, col2a = st.columns(2)
                    
                    if col1a.button(f"Switch to '{selected_db}'"):
                        st.session_state.connection_params['database'] = selected_db
                        success, message = refresh_data()
                        if success:
                            st.success(f"Switched to database '{selected_db}'")
                        else:
                            st.error(message)
                    
                    if col2a.button(f"Delete '{selected_db}'", type="primary"):
                        confirm = st.checkbox(f"Confirm deletion of database '{selected_db}'?")
                        if confirm:
                            try:
                                st.session_state.client.delete_database(selected_db)
                                st.success(f"Database '{selected_db}' deleted successfully")
                                # Refresh databases list
                                refresh_data()
                            except Exception as e:
                                st.error(f"Failed to delete database: {e}")
            else:
                st.info(f"No databases found for tenant '{st.session_state.connection_params['tenant']}'")
        
        with col2:
            st.subheader("Create New Database")
            
            with st.form("create_database_form"):
                database_name = st.text_input("Database Name")
                submit_button = st.form_submit_button("Create Database")
            
            if submit_button and database_name:
                try:
                    response = st.session_state.client.create_database(
                        database_name, tenant=st.session_state.connection_params['tenant']
                    )
                    st.success(f"Database '{database_name}' created successfully!")
                    # Refresh databases list
                    refresh_data()
                except Exception as e:
                    st.error(f"Failed to create database: {e}")
    
    # Collections Tab - Just the basic structure
    with tabs[3]:
        st.header("Collection Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Collections")
            
            if st.session_state.collections:
                collections_df = pd.DataFrame([
                    {
                        "Name": c.get("name"),
                        "ID": c.get("id"),
                        "Dimension": c.get("dimension"),
                        "Has Metadata": "Yes" if c.get("metadata") else "No"
                    }
                    for c in st.session_state.collections
                ])
                
                st.dataframe(collections_df, use_container_width=True)
                
                # Collection selection
                collection_names = [c.get("name") for c in st.session_state.collections]
                selected_collection = st.selectbox(
                    "Select Collection", options=collection_names
                )
                
                if selected_collection:
                    # Find the collection object
                    collection = next(
                        (c for c in st.session_state.collections if c.get("name") == selected_collection),
                        None
                    )
                    
                    if collection:
                        st.session_state.current_collection = collection
                        
                        st.markdown("#### Collection Details")
                        st.json(collection)
                        
                        col1a, col2a = st.columns(2)
                        
                        if col1a.button("Browse Items", key="browse_items"):
                            st.info("Item browsing will be implemented in the next version")
                        
                        if col2a.button("Delete Collection", key="delete_collection"):
                            confirm = st.checkbox(f"Confirm deletion of collection '{selected_collection}'?")
                            if confirm:
                                try:
                                    st.session_state.client.delete_collection(
                                        selected_collection,
                                        database=st.session_state.connection_params['database'],
                                        tenant=st.session_state.connection_params['tenant']
                                    )
                                    st.success(f"Collection '{selected_collection}' deleted successfully")
                                    # Refresh collections list
                                    refresh_data()
                                except Exception as e:
                                    st.error(f"Failed to delete collection: {e}")
            else:
                st.info(f"No collections found in database '{st.session_state.connection_params['database']}'")
        
        with col2:
            st.subheader("Create New Collection")
            
            with st.form("create_collection_form"):
                collection_name = st.text_input("Collection Name")
                dimension = st.number_input("Dimension", min_value=1, value=768)
                metadata_json = st.text_area("Metadata (JSON, optional)")
                
                submit_button = st.form_submit_button("Create Collection")
            
            if submit_button and collection_name:
                # Parse metadata if provided
                metadata = None
                if metadata_json:
                    try:
                        metadata = json.loads(metadata_json)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in metadata")
                        metadata = None
                
                if collection_name:
                    try:
                        response = st.session_state.client.create_collection(
                            name=collection_name,
                            metadata=metadata,
                            dimension=dimension,
                            database=st.session_state.connection_params['database'],
                            tenant=st.session_state.connection_params['tenant']
                        )
                        st.success(f"Collection '{collection_name}' created successfully!")
                        # Refresh collections list
                        refresh_data()
                    except Exception as e:
                        st.error(f"Failed to create collection: {e}")
    
    # Query Tab - Placeholder
    with tabs[4]:
        st.header("Query Collection")
        st.info("The query interface will be implemented in the next version.")
        
        # You will implement this in the next steps
        st.markdown("""
        This tab will allow you to:
        - Select a collection to query
        - Enter text queries
        - Upload embeddings for querying
        - Visualize query results
        """)
    
    # Analytics Tab - Placeholder
    with tabs[5]:
        st.header("Analytics & Visualization")
        st.info("Analytics features will be implemented in the next version.")
        
        # You will implement this in the next steps
        st.markdown("""
        This tab will provide:
        - Embedding visualizations using UMAP/t-SNE
        - Collection statistics
        - Similarity analysis
        - Performance metrics
        """)


# Footer
st.markdown("---")
col1, col2 = st.columns([4, 1])
col1.caption("ChromaLens - A powerful interface for ChromaDB vector database management")
col2.caption(f"Version: 0.1.0")