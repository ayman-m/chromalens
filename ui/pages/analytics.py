"""
Analytics page for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from components.header import show_success, show_error, show_info, show_warning
from components.visualization import render_visualization_interface

def render_analytics_page():
    """Render the analytics page"""
    st.header("Analytics & Visualization")
    
    # Check if we have collections
    if not st.session_state.collections:
        st.warning("No collections available for analytics")
        
        # Show helpful message
        st.markdown("""
        You need to have at least one collection before you can run analytics.
        
        Options:
        1. Create a new collection in the Collections tab
        2. Connect to a different database with existing collections
        """)
        
        if st.button("Go to Collections"):
            st.session_state.current_page = "Collections"
            st.experimental_rerun()
            
        return
    
    # Analytics tabs
    tabs = st.tabs([
        "Embeddings Visualization", 
        "Metadata Analysis", 
        "Collection Stats",
        "Similarity Analysis"
    ])
    
    # Embeddings Visualization Tab
    with tabs[0]:
        render_embeddings_visualization()
    
    # Metadata Analysis Tab
    with tabs[1]:
        render_metadata_analysis()
    
    # Collection Stats Tab
    with tabs[2]:
        render_collection_stats()
    
    # Similarity Analysis Tab
    with tabs[3]:
        render_similarity_analysis()

def render_embeddings_visualization():
    """Render the embeddings visualization tab"""
    st.subheader("Embeddings Visualization")
    
    # Delegate to the visualization component
    render_visualization_interface()

def render_metadata_analysis():
    """Render the metadata analysis tab"""
    st.subheader("Metadata Analysis")
    
    # Collection selection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection", 
        options=collection_names,
        key="metadata_collection_select"
    )
    
    if not selected_collection:
        return
    
    # Try to get metadata fields
    try:
        # Get a sample of items
        sample_items = st.session_state.client.get_items(
            collection_name=selected_collection,
            limit=20,
            include_embeddings=False,
            database=st.session_state.connection_params['database'],
            tenant=st.session_state.connection_params['tenant']
        )
        
        # Extract metadata fields
        metadata_fields = set()
        if sample_items and "metadatas" in sample_items:
            for metadata in sample_items["metadatas"]:
                if metadata:
                    metadata_fields.update(metadata.keys())
        
        if not metadata_fields:
            st.info("No metadata fields found in this collection")
            return
        
        # Let user select fields to analyze
        selected_fields = st.multiselect(
            "Select Metadata Fields to Analyze",
            options=list(metadata_fields),
            default=list(metadata_fields)[:min(3, len(metadata_fields))]
        )
        
        if not selected_fields:
            st.info("Select at least one field to analyze")
            return
        
        # Get a larger sample for analysis
        with st.spinner("Loading data for analysis..."):
            items = st.session_state.client.get_items(
                collection_name=selected_collection,
                limit=1000,  # Adjust based on your performance needs
                include_embeddings=False,
                database=st.session_state.connection_params['database'],
                tenant=st.session_state.connection_params['tenant']
            )
            
            if not items or "metadatas" not in items or not items["metadatas"]:
                st.warning("No items found in collection")
                return
            
            # Show metadata analysis
            for field in selected_fields:
                # Extract field values
                field_values = []
                for metadata in items["metadatas"]:
                    if metadata and field in metadata:
                        field_values.append(metadata[field])
                
                # Skip if no values found
                if not field_values:
                    st.info(f"No values found for field '{field}'")
                    continue
                
                # Analyze field
                analyze_metadata_field(field, field_values)
    
    except Exception as e:
        st.error(f"Error analyzing metadata: {e}")

def analyze_metadata_field(field_name, field_values):
    """Analyze a single metadata field"""
    st.markdown(f"### Field: `{field_name}`")
    
    # Determine field type
    field_types = set(type(value).__name__ for value in field_values)
    st.caption(f"Data types: {', '.join(field_types)}")
    
    # Analyze based on type
    if all(isinstance(value, (int, float)) for value in field_values):
        # Numeric field
        numeric_values = [float(value) for value in field_values]
        
        # Basic stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean", f"{np.mean(numeric_values):.2f}")
        col2.metric("Median", f"{np.median(numeric_values):.2f}")
        col3.metric("Min", f"{min(numeric_values):.2f}")
        col4.metric("Max", f"{max(numeric_values):.2f}")
        
        # Histogram
        fig = px.histogram(
            numeric_values,
            title=f"Distribution of '{field_name}'",
            labels={'x': field_name, 'y': 'Count'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif all(isinstance(value, str) for value in field_values):
        # String field
        value_counts = {}
        for value in field_values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        # Sort by frequency
        sorted_counts = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Basic stats
        st.metric("Unique Values", len(value_counts))
        
        # Create bar chart for top values
        top_n = min(20, len(sorted_counts))
        labels = [item[0] for item in sorted_counts[:top_n]]
        values = [item[1] for item in sorted_counts[:top_n]]
        
        fig = px.bar(
            x=labels,
            y=values,
            title=f"Most Common Values for '{field_name}' (Top {top_n})",
            labels={'x': field_name, 'y': 'Count'}
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # Mixed type or other
        st.info(f"Field '{field_name}' has mixed types. Analysis limited.")
        
        # Show a table of the most common values
        value_counts = {}
        for value in field_values:
            str_value = str(value)
            value_counts[str_value] = value_counts.get(str_value, 0) + 1
            
        # Sort by frequency    
        sorted_counts = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create dataframe for display
        top_n = min(20, len(sorted_counts))
        counts_df = pd.DataFrame(
            sorted_counts[:top_n], 
            columns=["Value", "Count"]
        )
        
        st.dataframe(counts_df, use_container_width=True)

def render_collection_stats():
    """Render the collection stats tab"""
    st.subheader("Collection Statistics")
    
    # Collection selection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection", 
        options=collection_names,
        key="stats_collection_select"
    )
    
    if not selected_collection:
        return
    
    # Show statistics
    if st.button("Load Collection Statistics", key="load_stats_button"):
        with st.spinner("Loading collection statistics..."):
            try:
                # Get collection stats
                stats = st.session_state.client.get_collection_stats(
                    collection_name=selected_collection,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                if not stats:
                    st.warning("No statistics available for this collection")
                    return
                
                # Display basic stats
                col1, col2, col3 = st.columns(3)
                
                col1.metric("Total Documents", stats.get("count", 0))
                col2.metric("Embedding Dimension", stats.get("dimension", 0))
                col3.metric("Collection Size", f"{stats.get('size_mb', 0):.2f} MB")
                
                # Display document length distribution if available
                if "document_lengths" in stats:
                    st.subheader("Document Length Distribution")
                    
                    fig = px.histogram(
                        x=stats["document_lengths"],
                        nbins=50,
                        title="Document Length Distribution",
                        labels={'x': 'Document Length (chars)', 'y': 'Count'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display detailed stats
                st.subheader("Detailed Statistics")
                
                # Convert stats to pretty format
                pretty_stats = {}
                for key, value in stats.items():
                    # Skip arrays that would be too large
                    if isinstance(value, list) and len(value) > 100:
                        pretty_stats[key] = f"List with {len(value)} items"
                    else:
                        pretty_stats[key] = value
                
                st.json(pretty_stats)
                
            except Exception as e:
                st.error(f"Failed to load collection statistics: {e}")

def render_similarity_analysis():
    """Render the similarity analysis tab"""
    st.subheader("Similarity Analysis")
    
    st.markdown("""
    This feature allows you to analyze similarity between documents or query items to find patterns and relationships.
    """)
    
    # Collection selection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection", 
        options=collection_names,
        key="similarity_collection_select"
    )
    
    if not selected_collection:
        return
    
    # Analysis type
    analysis_type = st.radio(
        "Analysis Type",
        options=["Document Similarity", "Query Comparison", "Nearest Neighbors"],
        horizontal=True
    )
    
    if analysis_type == "Document Similarity":
        st.info("Document similarity analysis will be available in the next version.")
        
    elif analysis_type == "Query Comparison":
        st.subheader("Query Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            query1 = st.text_area("Query 1", height=100)
        
        with col2:
            query2 = st.text_area("Query 2", height=100)
        
        if st.button("Compare Queries") and query1 and query2:
            st.info("Query comparison will be available in the next version.")
            
    elif analysis_type == "Nearest Neighbors":
        st.subheader("Nearest Neighbors Analysis")
        
        # Sample size
        sample_size = st.slider(
            "Sample Size", 
            min_value=5, 
            max_value=100, 
            value=20,
            help="Number of items to sample from the collection"
        )
        
        # Get neighbors
        n_neighbors = st.slider(
            "Neighbors to Find", 
            min_value=2, 
            max_value=20, 
            value=5
        )
        
        if st.button("Run Nearest Neighbors Analysis"):
            st.info("Nearest neighbors analysis will be available in the next version.")