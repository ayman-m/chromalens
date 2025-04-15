"""
Connection management component for ChromaLens UI
"""

import streamlit as st
from datetime import datetime

from chromalens.client.client import ChromaLensClient
from components.header import show_success, show_info, show_error, show_warning

def initialize_connection_state():
    """Initialize connection-related session state variables"""
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

def connect_to_chroma():
    """Connect to ChromaDB server with current connection parameters"""
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

def disconnect_from_chroma():
    """Disconnect from ChromaDB server"""
    st.session_state.client = None
    st.session_state.connected = False
    return True, "Disconnected from server"

def refresh_data():
    """Refresh data from ChromaDB server"""
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

def render_connection_form():
    """Render the connection form"""
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
            show_success(message)
        else:
            show_error(message)
    
    if disconnect_button:
        success, message = disconnect_from_chroma()
        if success:
            show_info(message)

def render_connection_status():
    """Render the connection status and tenant/database selection"""
    if st.session_state.connected:
        show_success("✅ Connected")
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
                show_success(message)
            else:
                show_error(message)
    
    else:
        show_warning("❌ Not connected")

def render_connection_sidebar():
    """Render the connection sidebar"""
    st.subheader("Connection Settings")
    
    # Connection form
    render_connection_form()
    
    # Show connection status
    render_connection_status()
    
    # About section
    st.sidebar.markdown("---")
    st.sidebar.subheader("About ChromaLens")
    st.sidebar.markdown(
        "ChromaLens is an open-source tool for managing and visualizing "
        "ChromaDB vector databases. Learn more on [GitHub](https://github.com/ayman-m/chromalens)."
    )