"""
Query interface components for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import time
from io import StringIO

from components.header import show_success, show_error, show_info, show_warning

def render_query_interface():
    """Render the query interface for collections"""
    if not st.session_state.collections:
        show_warning("No collections available for querying")
        return
    
    # Collection selection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection to Query", 
        options=collection_names,
        key="query_collection_select"
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
    
    # Query tabs
    query_tabs = st.tabs(["Text Query", "Vector Query", "Hybrid Query", "Batch Query"])
    
    # Text Query Tab
    with query_tabs[0]:
        render_text_query(selected_collection, collection)
    
    # Vector Query Tab
    with query_tabs[1]:
        render_vector_query(selected_collection, collection)
    
    # Hybrid Query Tab
    with query_tabs[2]:
        render_hybrid_query(selected_collection, collection)
    
    # Batch Query Tab
    with query_tabs[3]:
        render_batch_query(selected_collection, collection)

def render_text_query(collection_name, collection):
    """Render text-based query interface"""
    st.subheader("Text Query")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query_text = st.text_area("Enter your query text", height=100)
    
    with col2:
        n_results = st.number_input("Number of results", min_value=1, max_value=100, value=5)
        include_embeddings = st.checkbox("Include embeddings", value=False)
        include_documents = st.checkbox("Include documents", value=True)
        include_metadata = st.checkbox("Include metadata", value=True)
    
    # Metadata filtering
    with st.expander("Metadata Filtering"):
        filter_json = st.text_area(
            "Filter (JSON format)",
            help="Example: {\"category\": {\"$eq\": \"blog\"}} or {\"year\": {\"$gte\": 2020}}"
        )
    
    # Execute query
    if st.button("Execute Query", key="execute_text_query"):
        if not query_text:
            show_warning("Please enter query text")
            return
        
        # Process filter if provided
        where_filter = None
        if filter_json:
            try:
                where_filter = json.loads(filter_json)
            except json.JSONDecodeError:
                show_error("Invalid JSON in filter")
                return
        
        # Show a spinner while processing
        with st.spinner("Querying collection..."):
            try:
                start_time = time.time()
                
                # Execute query
                results = st.session_state.client.query_collection(
                    collection_name=collection_name,
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where_filter,
                    include_embeddings=include_embeddings,
                    include_documents=include_documents,
                    include_metadata=include_metadata,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                end_time = time.time()
                query_time = end_time - start_time
                
                # Display results
                display_query_results(results, query_time, include_embeddings)
                
            except Exception as e:
                show_error(f"Query failed: {e}")

def render_vector_query(collection_name, collection):
    """Render vector-based query interface"""
    st.subheader("Vector Query")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        vector_input = st.text_area(
            "Enter vector values (comma-separated or JSON array)",
            height=100,
            help="Example: [0.1, 0.2, 0.3, ...] or 0.1, 0.2, 0.3, ..."
        )
    
    with col2:
        n_results = st.number_input("Number of results", min_value=1, max_value=100, value=5, key="vector_n_results")
        include_embeddings = st.checkbox("Include embeddings", value=False, key="vector_include_embeddings")
        include_documents = st.checkbox("Include documents", value=True, key="vector_include_documents")
        include_metadata = st.checkbox("Include metadata", value=True, key="vector_include_metadata")
    
    # Metadata filtering
    with st.expander("Metadata Filtering"):
        filter_json = st.text_area(
            "Filter (JSON format)",
            help="Example: {\"category\": {\"$eq\": \"blog\"}} or {\"year\": {\"$gte\": 2020}}",
            key="vector_filter_json"
        )
    
    # Execute query
    if st.button("Execute Query", key="execute_vector_query"):
        if not vector_input:
            show_warning("Please enter vector values")
            return
        
        # Parse vector input
        try:
            if vector_input.startswith('[') and vector_input.endswith(']'):
                # Parse as JSON array
                query_vector = json.loads(vector_input)
            else:
                # Parse as comma-separated values
                query_vector = [float(x.strip()) for x in vector_input.split(',') if x.strip()]
            
            # Verify vector dimension matches collection
            expected_dim = collection.get('dimension')
            if expected_dim and len(query_vector) != expected_dim:
                show_error(f"Vector dimension mismatch. Expected {expected_dim}, got {len(query_vector)}")
                return
        except Exception as e:
            show_error(f"Invalid vector format: {e}")
            return
        
        # Process filter if provided
        where_filter = None
        if filter_json:
            try:
                where_filter = json.loads(filter_json)
            except json.JSONDecodeError:
                show_error("Invalid JSON in filter")
                return
        
        # Show a spinner while processing
        with st.spinner("Querying collection..."):
            try:
                start_time = time.time()
                
                # Execute query
                results = st.session_state.client.query_collection(
                    collection_name=collection_name,
                    query_embeddings=[query_vector],
                    n_results=n_results,
                    where=where_filter,
                    include_embeddings=include_embeddings,
                    include_documents=include_documents,
                    include_metadata=include_metadata,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                end_time = time.time()
                query_time = end_time - start_time
                
                # Display results
                display_query_results(results, query_time, include_embeddings)
                
            except Exception as e:
                show_error(f"Query failed: {e}")

def render_hybrid_query(collection_name, collection):
    """Render hybrid query interface (text + metadata)"""
    st.subheader("Hybrid Query")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query_text = st.text_area("Enter your query text", height=100, key="hybrid_query_text")
    
    with col2:
        n_results = st.number_input("Number of results", min_value=1, max_value=100, value=5, key="hybrid_n_results")
        alpha = st.slider("Alpha (keyword weight)", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
        include_embeddings = st.checkbox("Include embeddings", value=False, key="hybrid_include_embeddings")
        include_documents = st.checkbox("Include documents", value=True, key="hybrid_include_documents")
        include_metadata = st.checkbox("Include metadata", value=True, key="hybrid_include_metadata")
    
    # Metadata filtering
    with st.expander("Metadata Filtering"):
        filter_json = st.text_area(
            "Filter (JSON format)",
            help="Example: {\"category\": {\"$eq\": \"blog\"}} or {\"year\": {\"$gte\": 2020}}",
            key="hybrid_filter_json"
        )
    
    # Execute query
    if st.button("Execute Query", key="execute_hybrid_query"):
        if not query_text:
            show_warning("Please enter query text")
            return
        
        # Process filter if provided
        where_filter = None
        if filter_json:
            try:
                where_filter = json.loads(filter_json)
            except json.JSONDecodeError:
                show_error("Invalid JSON in filter")
                return
        
        # Show a spinner while processing
        with st.spinner("Querying collection..."):
            try:
                start_time = time.time()
                
                # Execute hybrid query
                results = st.session_state.client.query_collection(
                    collection_name=collection_name,
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where_filter,
                    include_embeddings=include_embeddings,
                    include_documents=include_documents,
                    include_metadata=include_metadata,
                    alpha=alpha,  # Hybrid search parameter
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                end_time = time.time()
                query_time = end_time - start_time
                
                # Display results
                display_query_results(results, query_time, include_embeddings)
                
            except Exception as e:
                show_error(f"Query failed: {e}")

def render_batch_query(collection_name, collection):
    """Render batch query interface"""
    st.subheader("Batch Query")
    
    # Upload CSV file with queries
    st.write("Upload a CSV file with queries")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="batch_csv_upload")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if uploaded_file is not None:
            # Read CSV content
            csv_content = uploaded_file.getvalue().decode("utf-8")
            df = pd.read_csv(StringIO(csv_content))
            
            # Display preview
            st.write("Preview:")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Select query column
            query_column = st.selectbox("Select column with queries", options=df.columns)
        else:
            st.info("Please upload a CSV file with query texts")
            query_column = None
    
    with col2:
        if uploaded_file is not None:
            n_results = st.number_input("Number of results per query", min_value=1, max_value=100, value=5, key="batch_n_results")
            include_embeddings = st.checkbox("Include embeddings", value=False, key="batch_include_embeddings")
            include_documents = st.checkbox("Include documents", value=True, key="batch_include_documents")
            include_metadata = st.checkbox("Include metadata", value=True, key="batch_include_metadata")
    
    # Metadata filtering
    if uploaded_file is not None:
        with st.expander("Metadata Filtering"):
            filter_json = st.text_area(
                "Filter (JSON format)",
                help="Example: {\"category\": {\"$eq\": \"blog\"}} or {\"year\": {\"$gte\": 2020}}",
                key="batch_filter_json"
            )
    
    # Execute batch query
    if uploaded_file is not None and query_column and st.button("Execute Batch Query", key="execute_batch_query"):
        # Get queries from selected column
        queries = df[query_column].tolist()
        
        if not queries:
            show_warning("No queries found in selected column")
            return
        
        # Process filter if provided
        where_filter = None
        if filter_json:
            try:
                where_filter = json.loads(filter_json)
            except json.JSONDecodeError:
                show_error("Invalid JSON in filter")
                return
        
        # Show a spinner while processing
        with st.spinner(f"Processing {len(queries)} queries..."):
            try:
                start_time = time.time()
                
                # Execute batch query
                results = st.session_state.client.query_collection(
                    collection_name=collection_name,
                    query_texts=queries,
                    n_results=n_results,
                    where=where_filter,
                    include_embeddings=include_embeddings,
                    include_documents=include_documents,
                    include_metadata=include_metadata,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                end_time = time.time()
                query_time = end_time - start_time
                
                # Display results
                st.success(f"Batch query completed in {query_time:.2f} seconds")
                
                # Create a downloadable CSV with results
                if results and len(results.get('ids', [])) > 0:
                    all_results = []
                    
                    for i, query in enumerate(queries):
                        if i < len(results.get('ids', [])):
                            query_results = {
                                'query': query,
                                'results': results.get('ids')[i],
                                'documents': results.get('documents', [[]])[i] if results.get('documents') else None,
                                'distances': results.get('distances', [[]])[i] if results.get('distances') else None,
                                'metadatas': results.get('metadatas', [[]])[i] if results.get('metadatas') else None
                            }
                            all_results.append(query_results)
                    
                    # Display summary
                    st.write(f"Total queries: {len(queries)}")
                    st.write(f"Queries with results: {len(all_results)}")
                    
                    # Create downloadable results
                    st.download_button(
                        "Download Results as JSON",
                        data=json.dumps(all_results, indent=2),
                        file_name=f"batch_results_{collection_name}.json",
                        mime="application/json"
                    )
                else:
                    show_warning("No results found for batch query")
                
            except Exception as e:
                show_error(f"Batch query failed: {e}")

def display_query_results(results, query_time, include_embeddings=False):
    """Display formatted query results"""
    if not results or len(results.get('ids', [])) == 0:
        show_info("No results found")
        return
    
    st.success(f"Query completed in {query_time:.4f} seconds")
    
    # Get result components
    ids = results.get('ids', [[]])[0]
    distances = results.get('distances', [[]])[0]
    documents = results.get('documents', [[]])[0] if results.get('documents') else None
    metadatas = results.get('metadatas', [[]])[0] if results.get('metadatas') else None
    embeddings = results.get('embeddings', [[]])[0] if include_embeddings and results.get('embeddings') else None
    
    # Create result items
    for i in range(len(ids)):
        with st.container():
            st.markdown(f"### Result {i+1}")
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**ID:** `{ids[i]}`")
                st.markdown(f"**Distance:** `{distances[i]:.6f}`")
                st.markdown(f"**Similarity:** `{1 - distances[i]:.2%}`")
            
            with col2:
                if documents:
                    st.markdown("**Document:**")
                    st.markdown(f"```\n{documents[i]}\n```")
                
                if metadatas and i < len(metadatas):
                    st.markdown("**Metadata:**")
                    st.json(metadatas[i])
            
            if embeddings and i < len(embeddings):
                with st.expander("Show Embedding Vector"):
                    embedding_df = pd.DataFrame({
                        'Dimension': list(range(len(embeddings[i]))),
                        'Value': embeddings[i]
                    })
                    st.dataframe(embedding_df, use_container_width=False)
            
            st.markdown("---")