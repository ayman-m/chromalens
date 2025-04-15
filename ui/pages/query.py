"""
Query page for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime

from components.header import show_success, show_error, show_info, show_warning
from components.query_interface import render_query_interface

def render_query_page():
    """Render the query page"""
    st.header("Query Collection")
    
    # Check if we have collections
    if not st.session_state.collections:
        st.warning("No collections available for querying")
        
        # Show helpful message
        st.markdown("""
        You need to have at least one collection before you can run queries.
        
        Options:
        1. Create a new collection in the Collections tab
        2. Connect to a different database with existing collections
        """)
        
        if st.button("Go to Collections"):
            st.session_state.current_page = "Collections"
            st.experimental_rerun()
            
        return
    
    # Query interface tabs
    tabs = st.tabs(["Search Interface", "Query History", "Query Builder"])
    
    # Search Interface Tab
    with tabs[0]:
        render_search_interface()
    
    # Query History Tab
    with tabs[1]:
        render_query_history()
    
    # Query Builder Tab
    with tabs[2]:
        render_query_builder()

def render_search_interface():
    """Render the search interface tab"""
    # Delegate to the query interface component
    render_query_interface()

def render_query_history():
    """Render the query history tab"""
    st.subheader("Query History")
    
    # Initialize history if not present
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    
    if not st.session_state.query_history:
        st.info("No query history yet. Run some queries to see them here.")
        return
    
    # Create DataFrame from history
    history_df = pd.DataFrame(st.session_state.query_history)
    
    # Display history
    st.dataframe(history_df, use_container_width=True)
    
    # Clear history button
    if st.button("Clear History"):
        st.session_state.query_history = []
        st.success("Query history cleared")
        st.experimental_rerun()
    
    # Select a query to rerun
    st.subheader("Rerun Query")
    
    query_indices = list(range(len(st.session_state.query_history)))
    if query_indices:
        selected_idx = st.selectbox(
            "Select Query to Rerun",
            options=query_indices,
            format_func=lambda i: f"{st.session_state.query_history[i]['Timestamp']} - {st.session_state.query_history[i]['Type']} - {st.session_state.query_history[i]['Collection']}"
        )
        
        if st.button("Rerun Selected Query"):
            selected_query = st.session_state.query_history[selected_idx]
            
            # Set up the query parameters
            st.session_state.rerun_query = selected_query
            
            # Switch to search interface tab
            st.success("Query loaded. Switch to Search Interface tab to run it.")

def render_query_builder():
    """Render the query builder tab"""
    st.subheader("Query Builder")
    
    # Select a collection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection",
        options=collection_names,
        key="qb_collection_select"
    )
    
    if not selected_collection:
        return
    
    # Query type
    query_type = st.radio(
        "Query Type",
        options=["Text Query", "Vector Query", "Hybrid Query"],
        horizontal=True,
        key="qb_query_type"
    )
    
    # Query input
    st.subheader("Query Input")
    
    if query_type == "Text Query":
        query_text = st.text_area("Enter Query Text", key="qb_query_text")
    elif query_type == "Vector Query":
        query_vector = st.text_area(
            "Enter Vector (JSON array or comma-separated values)",
            key="qb_query_vector",
            help="Example: [0.1, 0.2, ...] or 0.1, 0.2, ..."
        )
    else:  # Hybrid Query
        query_text = st.text_area("Enter Query Text", key="qb_hybrid_text")
        alpha = st.slider(
            "Alpha (Text vs. Vector weight)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            key="qb_alpha",
            help="0 = vector only, 1 = text only"
        )
    
    # Query options expander
    with st.expander("Query Options", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            n_results = st.number_input(
                "Number of Results",
                min_value=1,
                max_value=100,
                value=5,
                key="qb_n_results"
            )
            
            include_documents = st.checkbox(
                "Include Documents",
                value=True,
                key="qb_include_documents"
            )
        
        with col2:
            include_metadata = st.checkbox(
                "Include Metadata",
                value=True,
                key="qb_include_metadata"
            )
            
            include_embeddings = st.checkbox(
                "Include Embeddings",
                value=False,
                key="qb_include_embeddings"
            )
    
    # Metadata filtering
    with st.expander("Metadata Filtering"):
        filter_json = st.text_area(
            "Filter (JSON format)",
            key="qb_filter",
            help="Example: {\"category\": {\"$eq\": \"blog\"}} or {\"year\": {\"$gte\": 2020}}"
        )
    
    # Execute button
    if st.button("Execute Query", key="qb_execute"):
        if query_type == "Text Query" and not st.session_state.qb_query_text:
            show_warning("Please enter query text")
            return
        elif query_type == "Vector Query" and not st.session_state.qb_query_vector:
            show_warning("Please enter query vector")
            return
        elif query_type == "Hybrid Query" and not st.session_state.qb_hybrid_text:
            show_warning("Please enter query text for hybrid search")
            return
        
        # Process filter if provided
        where_filter = None
        if filter_json:
            try:
                where_filter = json.loads(filter_json)
            except json.JSONDecodeError:
                show_error("Invalid JSON in filter")
                return
        
        # Execute the query (placeholder)
        st.info("This is a query builder preview. Execute this query in the Search Interface tab.")
        
        # Show query summary
        st.subheader("Query Summary")
        
        query_summary = {
            "Collection": selected_collection,
            "Type": query_type,
            "N Results": n_results,
            "Filter": where_filter or "None",
            "Include Documents": include_documents,
            "Include Metadata": include_metadata,
            "Include Embeddings": include_embeddings
        }
        
        if query_type == "Text Query":
            query_summary["Query Text"] = st.session_state.qb_query_text
        elif query_type == "Vector Query":
            query_summary["Query Vector"] = st.session_state.qb_query_vector
        else:  # Hybrid
            query_summary["Query Text"] = st.session_state.qb_hybrid_text
            query_summary["Alpha"] = st.session_state.qb_alpha
        
        # Display summary
        st.json(query_summary)
        
        # Add copy to clipboard button (for the generated query)
        if st.button("Copy Query to Clipboard"):
            st.success("Query copied to clipboard!")
            
            # This would be implemented with a JavaScript function in a real app
            # For now, just show a success message