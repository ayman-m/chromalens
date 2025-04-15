"""
Collection management components for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import json

from components.header import show_success, show_error, show_info
from components.connection import refresh_data

def render_collection_list():
    """Render a list of collections with actions"""
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
            return selected_collection
    else:
        st.info(f"No collections found in database '{st.session_state.connection_params['database']}'")
        return None

def render_collection_details(collection_name):
    """Render details for a specific collection"""
    if not collection_name:
        return
    
    # Find the collection object
    collection = next(
        (c for c in st.session_state.collections if c.get("name") == collection_name),
        None
    )
    
    if collection:
        st.session_state.current_collection = collection
        
        # Collection details in expandable section
        with st.expander("Collection Details", expanded=False):
            st.json(collection)
        
        col1, col2, col3 = st.columns(3)
        
        if col1.button("Browse Items", key="browse_items"):
            st.session_state.show_collection_items = True
        
        if col2.button("Get Collection Stats", key="get_stats"):
            try:
                # You'll implement this in the client
                stats = st.session_state.client.get_collection_stats(
                    collection_name,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                st.session_state.collection_stats = stats
                st.session_state.show_collection_stats = True
            except Exception as e:
                show_error(f"Failed to get collection stats: {e}")
                st.session_state.show_collection_stats = False
        
        if col3.button("Delete Collection", key="delete_collection"):
            st.session_state.confirm_delete = True
            
        if st.session_state.get('confirm_delete', False):
            confirm = st.checkbox(f"Confirm deletion of collection '{collection_name}'?")
            if confirm:
                try:
                    st.session_state.client.delete_collection(
                        collection_name,
                        database=st.session_state.connection_params['database'],
                        tenant=st.session_state.connection_params['tenant']
                    )
                    show_success(f"Collection '{collection_name}' deleted successfully")
                    # Reset state
                    st.session_state.confirm_delete = False
                    st.session_state.current_collection = None
                    # Refresh collections list
                    refresh_data()
                    st.experimental_rerun()
                except Exception as e:
                    show_error(f"Failed to delete collection: {e}")
        
        # Show collection items if requested
        if st.session_state.get('show_collection_items', False):
            display_collection_items(collection_name)
        
        # Show collection stats if requested
        if st.session_state.get('show_collection_stats', False) and st.session_state.get('collection_stats'):
            display_collection_stats(st.session_state.collection_stats)

def display_collection_items(collection_name, limit=100):
    """Display items in a collection"""
    st.subheader(f"Items in Collection: {collection_name}")
    
    # Add filtering options
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("Limit", min_value=1, max_value=1000, value=100)
    with col2:
        include_embeddings = st.checkbox("Include Embeddings", value=False)
    
    if st.button("Load Items", key="load_items"):
        try:
            # Get collection items (you'll implement this in the client)
            items = st.session_state.client.get_items(
                collection_name=collection_name,
                limit=limit,
                include_embeddings=include_embeddings,
                database=st.session_state.connection_params['database'],
                tenant=st.session_state.connection_params['tenant']
            )
            
            if not items or len(items.get('ids', [])) == 0:
                show_info("Collection is empty")
                return
            
            # Process items
            ids = items.get('ids', [])
            documents = items.get('documents', [])
            metadatas = items.get('metadatas', [])
            embeddings = items.get('embeddings', []) if include_embeddings else []
            
            # Create DataFrame for display
            items_data = []
            for i in range(len(ids)):
                item = {
                    "ID": ids[i],
                    "Document": documents[i] if i < len(documents) else None,
                    "Metadata": json.dumps(metadatas[i]) if i < len(metadatas) else None
                }
                if include_embeddings and i < len(embeddings):
                    item["Embedding"] = f"Vector[{len(embeddings[i])}]"
                items_data.append(item)
            
            items_df = pd.DataFrame(items_data)
            st.dataframe(items_df, use_container_width=True)
            
            # Add download button for the data
            csv = items_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download as CSV",
                csv,
                f"{collection_name}_items.csv",
                "text/csv",
                key="download_csv"
            )
            
        except Exception as e:
            show_error(f"Failed to load items: {e}")

def display_collection_stats(stats):
    """Display statistics for a collection"""
    st.subheader("Collection Statistics")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", stats.get('count', 0))
    col2.metric("Dimension", stats.get('dimension', 0))
    col3.metric("Avg. Document Length", stats.get('avg_document_length', 0))
    
    # Display metadata distribution if available
    if 'metadata_distribution' in stats:
        st.subheader("Metadata Distribution")
        for field, values in stats['metadata_distribution'].items():
            st.write(f"**{field}**")
            distribution_df = pd.DataFrame({
                "Value": list(values.keys()),
                "Count": list(values.values())
            })
            distribution_df = distribution_df.sort_values("Count", ascending=False)
            st.bar_chart(distribution_df.set_index("Value"))

def render_create_collection_form():
    """Render a form to create a new collection"""
    st.subheader("Create New Collection")
    
    with st.form("create_collection_form"):
        collection_name = st.text_input("Collection Name")
        dimension = st.number_input("Dimension", min_value=1, value=768)
        
        # Embedding function options
        embedding_options = [
            "None (Manual Embeddings)",
            "OpenAI",
            "Cohere", 
            "Hugging Face",
            "SentenceTransformers",
            "Custom"
        ]
        
        embedding_type = st.selectbox(
            "Embedding Function", 
            options=embedding_options,
            index=0
        )
        
        # Show relevant options based on embedding type
        if embedding_type == "OpenAI":
            model = st.selectbox(
                "Model", 
                options=["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
            )
            api_key = st.text_input("API Key", type="password")
        elif embedding_type == "Cohere":
            model = st.selectbox(
                "Model", 
                options=["embed-english-v2.0", "embed-multilingual-v2.0"]
            )
            api_key = st.text_input("API Key", type="password")
        elif embedding_type in ["Hugging Face", "SentenceTransformers"]:
            model = st.text_input(
                "Model Name", 
                value="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        metadata_json = st.text_area("Metadata (JSON, optional)")
        
        submit_button = st.form_submit_button("Create Collection")
    
    if submit_button and collection_name:
        # Parse metadata if provided
        metadata = None
        if metadata_json:
            try:
                metadata = json.loads(metadata_json)
            except json.JSONDecodeError:
                show_error("Invalid JSON in metadata")
                metadata = None
        
        # Create embedding function config if selected
        embedding_function = None
        if embedding_type != "None (Manual Embeddings)":
            embedding_function = {
                "type": embedding_type.lower().replace(" ", "_"),
            }
            
            if embedding_type in ["OpenAI", "Cohere"]:
                embedding_function["model"] = model
                embedding_function["api_key"] = api_key
            elif embedding_type in ["Hugging Face", "SentenceTransformers"]:
                embedding_function["model_name"] = model
        
        if collection_name:
            try:
                response = st.session_state.client.create_collection(
                    name=collection_name,
                    metadata=metadata,
                    dimension=dimension,
                    embedding_function=embedding_function,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                show_success(f"Collection '{collection_name}' created successfully!")
                # Refresh collections list
                refresh_data()
            except Exception as e:
                show_error(f"Failed to create collection: {e}")