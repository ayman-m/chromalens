"""
Visualization components for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

from components.header import show_success, show_error, show_info, show_warning

def render_visualization_interface():
    """Render the visualization interface for collections"""
    if not st.session_state.collections:
        show_warning("No collections available for visualization")
        return
    
    # Collection selection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection", 
        options=collection_names,
        key="viz_collection_select"
    )
    
    if not selected_collection:
        return
    
    # Find the collection object
    collection = next(
        (c for c in st.session_state.collections if c.get("name") == selected_collection),
        None
    )
    
    if not collection:
        return
    
    # Visualization type tabs
    viz_tabs = st.tabs(["Embeddings Visualization", "Metadata Analysis", "Collection Stats"])
    
    # Embeddings Visualization Tab
    with viz_tabs[0]:
        render_embeddings_visualization(selected_collection, collection)
    
    # Metadata Analysis Tab
    with viz_tabs[1]:
        render_metadata_analysis(selected_collection, collection)
    
    # Collection Stats Tab
    with viz_tabs[2]:
        render_collection_stats(selected_collection, collection)

def render_embeddings_visualization(collection_name, collection):
    """Render embeddings visualization"""
    st.subheader("Embeddings Visualization")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sample size
        sample_size = st.slider(
            "Sample Size", 
            min_value=10, 
            max_value=1000, 
            value=200,
            help="Number of embeddings to visualize (large numbers may slow down the visualization)"
        )
        
        # Dimensionality reduction technique
        dim_reduction = st.radio(
            "Dimensionality Reduction",
            options=["PCA", "t-SNE", "UMAP"],
            horizontal=True
        )
    
    with col2:
        # Color by metadata field
        st.markdown("### Visualization Options")
        
        # Get metadata fields from sample items
        try:
            # Get a sample item to extract metadata fields
            sample_items = st.session_state.client.get_items(
                collection_name=collection_name,
                limit=1,
                include_embeddings=False,
                database=st.session_state.connection_params['database'],
                tenant=st.session_state.connection_params['tenant']
            )
            
            metadata_fields = []
            if sample_items and "metadatas" in sample_items and sample_items["metadatas"]:
                metadata_fields = list(sample_items["metadatas"][0].keys())
            
            color_field = st.selectbox(
                "Color by Metadata Field",
                options=["None"] + metadata_fields,
                index=0
            )
        
        except Exception as e:
            st.error(f"Error loading metadata fields: {e}")
            color_field = "None"
        
        # Visualization parameters
        if dim_reduction == "t-SNE":
            perplexity = st.slider("Perplexity", min_value=5, max_value=50, value=30)
        elif dim_reduction == "UMAP":
            n_neighbors = st.slider("Neighbors", min_value=2, max_value=200, value=15)
            min_dist = st.slider("Min Distance", min_value=0.0, max_value=0.99, value=0.1, step=0.05)
    
    # Load and visualize embeddings
    if st.button("Generate Visualization", key="generate_viz"):
        with st.spinner(f"Loading and processing {sample_size} embeddings..."):
            try:
                # Get items with embeddings
                items = st.session_state.client.get_items(
                    collection_name=collection_name,
                    limit=sample_size,
                    include_embeddings=True,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                if not items or "embeddings" not in items or not items["embeddings"]:
                    show_warning("No embeddings found in this collection")
                    return
                
                # Extract embeddings and metadata
                embeddings = items["embeddings"]
                ids = items["ids"]
                
                # Create a matrix of embeddings
                embedding_matrix = np.array(embeddings)
                
                # Apply dimensionality reduction
                if dim_reduction == "PCA":
                    reducer = PCA(n_components=2)
                    reduced_data = reducer.fit_transform(embedding_matrix)
                    explained_variance = reducer.explained_variance_ratio_.sum()
                    technique_info = f"PCA (explained variance: {explained_variance:.2%})"
                
                elif dim_reduction == "t-SNE":
                    reducer = TSNE(n_components=2, perplexity=perplexity, random_state=42)
                    reduced_data = reducer.fit_transform(embedding_matrix)
                    technique_info = f"t-SNE (perplexity: {perplexity})"
                
                elif dim_reduction == "UMAP":
                    reducer = umap.UMAP(
                        n_components=2,
                        n_neighbors=n_neighbors,
                        min_dist=min_dist,
                        random_state=42
                    )
                    reduced_data = reducer.fit_transform(embedding_matrix)
                    technique_info = f"UMAP (neighbors: {n_neighbors}, min_dist: {min_dist})"
                
                # Create dataframe for plotting
                plot_df = pd.DataFrame({
                    'x': reduced_data[:, 0],
                    'y': reduced_data[:, 1],
                    'id': ids
                })
                
                # Add color by metadata if selected
                if color_field != "None" and "metadatas" in items and items["metadatas"]:
                    # Extract selected metadata field
                    color_values = []
                    for metadata in items["metadatas"]:
                        if color_field in metadata:
                            color_values.append(str(metadata[color_field]))
                        else:
                            color_values.append("N/A")
                    
                    plot_df['color'] = color_values
                    
                    # Create scatter plot with color
                    fig = px.scatter(
                        plot_df, 
                        x='x', 
                        y='y', 
                        color='color',
                        title=f"Embedding Visualization using {technique_info}",
                        labels={'color': color_field, 'x': 'Dimension 1', 'y': 'Dimension 2'},
                        hover_data=['id']
                    )
                else:
                    # Create scatter plot without color
                    fig = px.scatter(
                        plot_df, 
                        x='x', 
                        y='y', 
                        title=f"Embedding Visualization using {technique_info}",
                        labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
                        hover_data=['id']
                    )
                
                # Update layout
                fig.update_layout(
                    height=600,
                    width=800,
                    plot_bgcolor='rgba(240, 240, 240, 0.8)'
                )
                
                # Display the plot
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                show_error(f"Failed to generate visualization: {e}")

def render_metadata_analysis(collection_name, collection):
    """Render metadata analysis"""
    st.subheader("Metadata Analysis")
    
    try:
        # Get a sample of items to extract metadata fields
        sample_items = st.session_state.client.get_items(
            collection_name=collection_name,
            limit=100,
            include_embeddings=False,
            database=st.session_state.connection_params['database'],
            tenant=st.session_state.connection_params['tenant']
        )
        
        if not sample_items or "metadatas" not in sample_items or not sample_items["metadatas"]:
            show_warning("No metadata found in this collection")
            return
        
        # Extract all unique metadata fields
        metadata_fields = set()
        for metadata in sample_items["metadatas"]:
            metadata_fields.update(metadata.keys())
        
        if not metadata_fields:
            show_warning("No metadata fields found in this collection")
            return
        
        # Select field to analyze
        field_to_analyze = st.selectbox(
            "Select Metadata Field to Analyze",
            options=list(metadata_fields)
        )
        
        if not field_to_analyze:
            return
        
        # Analyze the selected field
        with st.spinner(f"Analyzing metadata field '{field_to_analyze}'..."):
            # Get items with the selected metadata field
            items = st.session_state.client.get_items(
                collection_name=collection_name,
                limit=1000,  # Increase for more accurate analysis
                include_embeddings=False,
                database=st.session_state.connection_params['database'],
                tenant=st.session_state.connection_params['tenant']
            )
            
            # Extract values for the selected field
            field_values = []
            for metadata in items["metadatas"]:
                if field_to_analyze in metadata:
                    field_values.append(metadata[field_to_analyze])
            
            if not field_values:
                show_warning(f"No values found for metadata field '{field_to_analyze}'")
                return
            
            # Analyze field value types
            field_types = set(type(value).__name__ for value in field_values)
            
            # Show field summary
            st.markdown(f"### Field: `{field_to_analyze}`")
            st.markdown(f"**Data Types:** {', '.join(field_types)}")
            st.markdown(f"**Total Values:** {len(field_values)}")
            
            # Analyze based on type
            if all(isinstance(value, (int, float)) for value in field_values):
                # Numeric analysis
                numeric_values = [float(value) for value in field_values]
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Mean", f"{sum(numeric_values) / len(numeric_values):.2f}")
                col2.metric("Min", f"{min(numeric_values):.2f}")
                col3.metric("Max", f"{max(numeric_values):.2f}")
                
                # Histogram
                fig = px.histogram(
                    x=numeric_values,
                    title=f"Distribution of '{field_to_analyze}' values",
                    labels={'x': field_to_analyze, 'y': 'Count'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            elif all(isinstance(value, str) for value in field_values):
                # String analysis - value frequency
                value_counts = {}
                for value in field_values:
                    value_counts[value] = value_counts.get(value, 0) + 1
                
                # Sort by frequency
                sorted_counts = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
                
                # Display as bar chart
                labels = [str(item[0]) for item in sorted_counts[:20]]  # Top 20
                values = [item[1] for item in sorted_counts[:20]]
                
                fig = px.bar(
                    x=labels,
                    y=values,
                    title=f"Most frequent values for '{field_to_analyze}' (top 20)",
                    labels={'x': field_to_analyze, 'y': 'Count'}
                )
                
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show total unique values
                st.info(f"Total unique values: {len(value_counts)}")
            
            else:
                # Mixed type - just show value frequency
                value_counts = {}
                for value in field_values:
                    str_value = str(value)
                    value_counts[str_value] = value_counts.get(str_value, 0) + 1
                
                # Sort by frequency
                sorted_counts = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
                
                # Display as table
                count_df = pd.DataFrame(sorted_counts[:50], columns=[field_to_analyze, 'Count'])
                st.dataframe(count_df, use_container_width=True)
    
    except Exception as e:
        show_error(f"Failed to analyze metadata: {e}")

def render_collection_stats(collection_name, collection):
    """Render collection statistics"""
    st.subheader("Collection Statistics")
    
    if st.button("Load Collection Statistics", key="load_collection_stats"):
        with st.spinner("Loading collection statistics..."):
            try:
                # Get collection stats
                stats = st.session_state.client.get_collection_stats(
                    collection_name=collection_name,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                if not stats:
                    show_warning("No statistics available for this collection")
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
                        title="Document Length Distribution",
                        labels={'x': 'Document Length (chars)', 'y': 'Count'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                show_error(f"Failed to load collection statistics: {e}")