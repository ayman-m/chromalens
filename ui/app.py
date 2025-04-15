"""
ChromaLens - A powerful user interface for ChromaDB vector database management.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import components
from components.header import render_header, show_success, show_error, show_info, show_warning
from components.connection import (
    initialize_connection_state,
    connect_to_chroma,
    refresh_data
)
from components.sidebar import render_sidebar

# Import pages
from pages.dashboard import render_dashboard
from pages.collections import render_collections_page
from pages.query import render_query_page
from pages.analytics import render_analytics_page
from pages.data_upload import render_data_upload_page

# App configuration
st.set_page_config(
    page_title="ChromaLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Render header with styling
render_header()

# Initialize session state variables
initialize_connection_state()

# Initialize page state if not already set
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Render sidebar
with st.sidebar:
    render_sidebar()

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
            
            # Connect to database
            success, message = connect_to_chroma()
            
            # Display result
            if success:
                show_success(message)
                st.experimental_rerun()
            else:
                show_error(message)

else:
    # Render the appropriate page based on navigation selection
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        render_dashboard()
    
    elif current_page == "Collections":
        render_collections_page()
    
    elif current_page == "Query":
        render_query_page()
    
    elif current_page == "Data Upload":
        render_data_upload_page()
    
    elif current_page == "Analytics":
        render_analytics_page()
    
    elif current_page == "Tenants":
        # For now, render directly here until we create a separate page module
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
                    show_success(f"Tenant '{tenant_name}' created successfully!")
                    # Refresh tenants list
                    refresh_data()
                except Exception as e:
                    show_error(f"Failed to create tenant: {e}")
    
    elif current_page == "Databases":
        # For now, render directly here until we create a separate page module
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
                            show_success(f"Switched to database '{selected_db}'")
                        else:
                            show_error(message)
                    
                    if col2a.button(f"Delete '{selected_db}'", type="primary"):
                        confirm = st.checkbox(f"Confirm deletion of database '{selected_db}'?")
                        if confirm:
                            try:
                                st.session_state.client.delete_database(selected_db)
                                show_success(f"Database '{selected_db}' deleted successfully")
                                # Refresh databases list
                                refresh_data()
                            except Exception as e:
                                show_error(f"Failed to delete database: {e}")
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
                    show_success(f"Database '{database_name}' created successfully!")
                    # Refresh databases list
                    refresh_data()
                except Exception as e:
                    show_error(f"Failed to create database: {e}")

# Footer
st.markdown("---")
col1, col2 = st.columns([4, 1])
col1.caption("ChromaLens - A powerful interface for ChromaDB vector database management")
col2.caption(f"Version: 0.1.0")