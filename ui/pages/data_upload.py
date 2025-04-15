"""
Data Upload page for ChromaLens UI
"""

import streamlit as st
import pandas as pd

from components.header import show_success, show_error, show_info, show_warning
from components.data_uploader import render_data_uploader

def render_data_upload_page():
    """Render the data upload page"""
    st.header("Upload Data")
    
    # Check if we have collections
    if not st.session_state.collections:
        st.warning("No collections available for data upload")
        
        # Show helpful message
        st.markdown("""
        You need to have at least one collection before you can upload data.
        
        Options:
        1. Create a new collection in the Collections tab
        2. Connect to a different database with existing collections
        """)
        
        if st.button("Create Collection"):
            st.session_state.current_page = "Collections"
            st.session_state.show_new_collection_form = True
            st.experimental_rerun()
            
        return
    
    # Upload tabs
    tabs = st.tabs([
        "Upload Interface", 
        "Embedding Configuration", 
        "Upload History",
        "Advanced Options"
    ])
    
    # Upload Interface Tab
    with tabs[0]:
        render_upload_interface()
    
    # Embedding Configuration Tab
    with tabs[1]:
        render_embedding_configuration()
    
    # Upload History Tab
    with tabs[2]:
        render_upload_history()
    
    # Advanced Options Tab
    with tabs[3]:
        render_advanced_options()

def render_upload_interface():
    """Render the upload interface tab"""
    # Delegate to the data uploader component
    render_data_uploader()

def render_embedding_configuration():
    """Render the embedding configuration tab"""
    st.subheader("Embedding Configuration")
    
    # Collection selection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection", 
        options=collection_names,
        key="embedding_collection_select"
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
    
    # Display current embedding function if available
    embedding_function = collection.get("metadata", {}).get("embedding_function")
    
    if embedding_function:
        st.success("This collection has an embedding function configured")
        
        # Display details
        st.json(embedding_function)
        
        # Option to update
        if st.button("Update Embedding Function"):
            st.session_state.update_embedding_function = True
    else:
        st.warning("This collection doesn't have an embedding function configured")
        
        # Option to add
        if st.button("Add Embedding Function"):
            st.session_state.update_embedding_function = True
    
    # Show embedding function form if requested
    if st.session_state.get("update_embedding_function", False):
        with st.form("embedding_function_form"):
            st.subheader("Embedding Function Configuration")
            
            # Embedding function options
            embedding_options = [
                "OpenAI",
                "Cohere", 
                "SentenceTransformers",
                "Hugging Face",
                "Custom"
            ]
            
            embedding_type = st.selectbox(
                "Embedding Function Type", 
                options=embedding_options
            )
            
            # Show relevant options based on embedding type
            if embedding_type == "OpenAI":
                model = st.selectbox(
                    "Model", 
                    options=["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
                )
                api_key = st.text_input("API Key", type="password")
                
                # Use key from settings if available
                if st.checkbox("Use API key from settings") and "openai_api_key" in st.session_state:
                    api_key = st.session_state.openai_api_key
                
            elif embedding_type == "Cohere":
                model = st.selectbox(
                    "Model", 
                    options=["embed-english-v2.0", "embed-multilingual-v2.0"]
                )
                api_key = st.text_input("API Key", type="password")
                
                # Use key from settings if available
                if st.checkbox("Use API key from settings") and "cohere_api_key" in st.session_state:
                    api_key = st.session_state.cohere_api_key
                
            elif embedding_type in ["SentenceTransformers", "Hugging Face"]:
                model = st.text_input(
                    "Model Name", 
                    value="sentence-transformers/all-MiniLM-L6-v2"
                )
                device = st.radio("Device", options=["cpu", "cuda"], horizontal=True)
                
            elif embedding_type == "Custom":
                custom_code = st.text_area(
                    "Custom Function (Python)",
                    height=200,
                    help="Enter Python code for a custom embedding function"
                )
            
            # Submit button
            submit_button = st.form_submit_button("Update Embedding Function")
            
            if submit_button:
                try:
                    # Create embedding function config
                    embedding_function = {
                        "type": embedding_type.lower().replace(" ", "_"),
                    }
                    
                    if embedding_type in ["OpenAI", "Cohere"]:
                        embedding_function["model"] = model
                        embedding_function["api_key"] = api_key
                    elif embedding_type in ["SentenceTransformers", "Hugging Face"]:
                        embedding_function["model_name"] = model
                        embedding_function["device"] = device
                    elif embedding_type == "Custom":
                        embedding_function["code"] = custom_code
                    
                    # Update collection with embedding function
                    # In a real implementation, this would call the client's update_collection method
                    
                    show_success(f"Embedding function updated for collection '{selected_collection}'")
                    st.session_state.update_embedding_function = False
                    
                except Exception as e:
                    show_error(f"Failed to update embedding function: {e}")
        
        # Cancel button
        if st.button("Cancel"):
            st.session_state.update_embedding_function = False
            st.experimental_rerun()

def render_upload_history():
    """Render the upload history tab"""
    st.subheader("Upload History")
    
    # Initialize upload history if not present
    if "upload_history" not in st.session_state:
        st.session_state.upload_history = []
    
    if not st.session_state.upload_history:
        st.info("No upload history yet. Upload some data to see it here.")
        return
    
    # Create DataFrame from history
    history_df = pd.DataFrame(st.session_state.upload_history)
    
    # Display history
    st.dataframe(history_df, use_container_width=True)
    
    # Clear history button
    if st.button("Clear History"):
        st.session_state.upload_history = []
        st.success("Upload history cleared")
        st.experimental_rerun()
    
    # Export history button
    if st.button("Export History"):
        # Convert to CSV
        csv = history_df.to_csv(index=False).encode('utf-8')
        
        # Create download button
        st.download_button(
            "Download History CSV",
            csv,
            "upload_history.csv",
            "text/csv",
            key="download_history"
        )

def render_advanced_options():
    """Render the advanced options tab"""
    st.subheader("Advanced Upload Options")
    
    # Batch size
    st.number_input(
        "Upload Batch Size",
        min_value=1,
        max_value=1000,
        value=100,
        help="Number of documents to upload in each batch"
    )
    
    # Preprocessing options
    st.subheader("Text Preprocessing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Strip HTML tags", value=True)
        st.checkbox("Convert to lowercase", value=False)
        st.checkbox("Remove extra whitespace", value=True)
    
    with col2:
        st.checkbox("Remove URLs", value=False)
        st.checkbox("Remove punctuation", value=False)
        st.checkbox("Remove stopwords", value=False)
    
    # Document chunking
    st.subheader("Document Chunking")
    
    enable_chunking = st.checkbox("Enable document chunking", value=False)
    
    if enable_chunking:
        chunk_size = st.number_input(
            "Maximum Chunk Size (characters)",
            min_value=100,
            max_value=10000,
            value=1000
        )
        
        chunk_overlap = st.number_input(
            "Chunk Overlap (characters)",
            min_value=0,
            max_value=500,
            value=100
        )
        
        chunk_strategy = st.radio(
            "Chunking Strategy",
            options=["By character", "By sentence", "By paragraph"],
            horizontal=True
        )
        
        st.info("Document chunking will be applied to text documents during upload")
    
    # Save options as defaults
    if st.button("Save as Defaults"):
        st.success("Options saved as defaults")
        
        # In a real application, these would be saved to session state
        # or a settings file