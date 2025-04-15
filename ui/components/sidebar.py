"""
Sidebar component for ChromaLens UI
"""

import streamlit as st
from datetime import datetime

from components.header import show_success, show_error, show_info, show_warning
from components.connection import render_connection_sidebar, refresh_data

def render_sidebar():
    """Render the complete sidebar with navigation and connection settings"""
    
    # App title and logo
    st.sidebar.title("ChromaLens")
    st.sidebar.caption("Vector DB Management")
    
    # Connection settings section
    with st.sidebar.expander("Connection", expanded=True):
        render_connection_sidebar()
    
    # Only show navigation when connected
    if st.session_state.connected:
        render_navigation()
    
    # Settings section
    with st.sidebar.expander("Settings", expanded=False):
        render_settings()
    
    # About section at the bottom
    st.sidebar.markdown("---")
    render_about_section()

def render_navigation():
    """Render the navigation section in the sidebar"""
    st.sidebar.markdown("## Navigation")
    
    # Navigation links
    selected = st.sidebar.radio(
        "Go to",
        options=[
            "Dashboard",
            "Collections",
            "Query",
            "Data Upload",
            "Analytics",
            "Tenants",
            "Databases"
        ],
        key="navigation"
    )
    
    # Store the selection in session state
    if "current_page" not in st.session_state or st.session_state.current_page != selected:
        st.session_state.current_page = selected
        
        # Force a rerun to update the UI based on the selected page
        # This will work when we switch to a page-based navigation
        # st.experimental_rerun()
    
    # Quick actions section
    st.sidebar.markdown("## Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    if col1.button("Refresh Data", key="sidebar_refresh"):
        success, message = refresh_data()
        if success:
            show_success(message)
        else:
            show_error(message)
    
    if col2.button("New Collection", key="sidebar_new_collection"):
        # Set the page to Collections and trigger new collection form
        st.session_state.current_page = "Collections"
        st.session_state.show_new_collection_form = True
        # Will be implemented when we have page-based navigation
        # st.experimental_rerun()

def render_settings():
    """Render the settings section in the sidebar"""
    # UI Theme
    st.sidebar.subheader("UI Settings")
    
    # Theme selection
    if "ui_theme" not in st.session_state:
        st.session_state.ui_theme = "Light"
        
    theme = st.sidebar.selectbox(
        "Theme",
        options=["Light", "Dark", "System Default"],
        index=["Light", "Dark", "System Default"].index(st.session_state.ui_theme),
        key="theme_select"
    )
    
    if theme != st.session_state.ui_theme:
        st.session_state.ui_theme = theme
        # Theme switching would be implemented here
        st.sidebar.info("Theme settings will be applied on reload")
    
    # API Keys management
    st.sidebar.subheader("API Keys")
    
    # Toggle for showing saved API keys
    if "show_api_keys" not in st.session_state:
        st.session_state.show_api_keys = False
        
    st.sidebar.checkbox(
        "Show saved API keys", 
        value=st.session_state.show_api_keys,
        key="toggle_api_keys",
        on_change=lambda: setattr(st.session_state, "show_api_keys", not st.session_state.show_api_keys)
    )
    
    # Display API keys if toggled on
    if st.session_state.show_api_keys:
        # OpenAI API Key
        openai_key = st.sidebar.text_input(
            "OpenAI API Key",
            value=st.session_state.get("openai_api_key", ""),
            type="password",
            key="openai_key_input"
        )
        
        if openai_key != st.session_state.get("openai_api_key", ""):
            st.session_state.openai_api_key = openai_key
            
        # Cohere API Key
        cohere_key = st.sidebar.text_input(
            "Cohere API Key",
            value=st.session_state.get("cohere_api_key", ""),
            type="password",
            key="cohere_key_input"
        )
        
        if cohere_key != st.session_state.get("cohere_api_key", ""):
            st.session_state.cohere_api_key = cohere_key

def render_about_section():
    """Render the about section in the sidebar"""
    st.sidebar.subheader("About ChromaLens")
    
    st.sidebar.markdown(
        """
        ChromaLens is an open-source tool for managing and visualizing 
        ChromaDB vector databases.
        
        [GitHub](https://github.com/ayman-m/chromalens) | 
        [Documentation](https://github.com/ayman-m/chromalens/docs)
        """
    )
    
    # Version info
    st.sidebar.caption("Version: 0.1.0")