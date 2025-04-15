"""
Collections page for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import json

from components.header import show_success, show_error, show_info, show_warning
from components.collection_manager import (
    render_collection_list,
    render_collection_details,
    render_create_collection_form
)

def render_collections_page():
    """Render the collections management page"""
    st.header("Collection Management")
    
    # Check if we should show the new collection form
    if st.session_state.get("show_new_collection_form", False):
        render_new_collection_tab()
        return
    
    # Show collection tabs
    tabs = st.tabs(["Browse Collections", "Create Collection", "Import/Export"])
    
    # Browse Collections tab
    with tabs[0]:
        render_browse_collections_tab()
    
    # Create Collection tab
    with tabs[1]:
        render_create_collection_tab()
    
    # Import/Export tab
    with tabs[2]:
        render_import_export_tab()

def render_new_collection_tab():
    """Render the new collection tab when directed from sidebar"""
    st.subheader("Create New Collection")
    
    render_create_collection_form()
    
    if st.button("Back to Collections"):
        st.session_state.show_new_collection_form = False
        st.experimental_rerun()

def render_browse_collections_tab():
    """Render the browse collections tab"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Collections")
        selected_collection = render_collection_list()
        if selected_collection:
            render_collection_details(selected_collection)
    
    with col2:
        # Show collection actions
        if not st.session_state.collections:
            st.info("No collections available")
            st.button("Create Your First Collection", on_click=lambda: setattr(st.session_state, "show_new_collection_form", True))
            return
        
        st.subheader("Collection Actions")
        
        # Filter collections
        search_term = st.text_input("Filter Collections", placeholder="Enter collection name...")
        
        if search_term:
            filtered_collections = [
                c for c in st.session_state.collections 
                if search_term.lower() in c.get("name", "").lower()
            ]
            
            if not filtered_collections:
                st.info(f"No collections found matching '{search_term}'")
            else:
                st.success(f"Found {len(filtered_collections)} matching collections")
                
                # Display filtered collections
                filtered_df = pd.DataFrame([
                    {"Name": c.get("name"), "Dimension": c.get("dimension")}
                    for c in filtered_collections
                ])
                
                st.dataframe(filtered_df, use_container_width=True)

def render_create_collection_tab():
    """Render the create collection tab"""
    st.subheader("Create New Collection")
    
    render_create_collection_form()

def render_import_export_tab():
    """Render the import/export tab"""
    st.subheader("Import/Export Collections")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Import section
        st.markdown("### Import Collection")
        
        import_options = st.radio(
            "Import Source",
            options=["JSON File", "CSV File", "Another ChromaDB"],
            horizontal=True
        )
        
        if import_options == "JSON File":
            uploaded_file = st.file_uploader("Upload JSON Collection", type=["json"])
            
            if uploaded_file is not None:
                try:
                    import_data = json.load(uploaded_file)
                    
                    # Display JSON structure
                    st.json(import_data)
                    
                    # Import options
                    with st.form("import_json_form"):
                        collection_name = st.text_input("Collection Name")
                        
                        # Additional options
                        create_embedding = st.checkbox("Generate Embeddings", value=True)
                        embedding_model = st.selectbox(
                            "Embedding Model",
                            options=["OpenAI", "Cohere", "SentenceTransformers"],
                            disabled=not create_embedding
                        )
                        
                        submit_button = st.form_submit_button("Import Collection")
                        
                        if submit_button:
                            # This would be implemented with actual import logic
                            st.success(f"Collection '{collection_name}' imported successfully!")
                            
                except Exception as e:
                    st.error(f"Error parsing JSON file: {e}")
        
        elif import_options == "CSV File":
            uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Display CSV preview
                    st.dataframe(df.head(), use_container_width=True)
                    
                    # Import options
                    with st.form("import_csv_form"):
                        collection_name = st.text_input("Collection Name")
                        
                        # Column mapping
                        document_col = st.selectbox("Document Column", options=df.columns)
                        id_col = st.selectbox("ID Column (optional)", options=["[Generate]"] + list(df.columns))
                        
                        # Metadata columns
                        metadata_cols = st.multiselect(
                            "Metadata Columns",
                            options=[col for col in df.columns if col != document_col and col != id_col]
                        )
                        
                        submit_button = st.form_submit_button("Import Collection")
                        
                        if submit_button:
                            # This would be implemented with actual import logic
                            st.success(f"Collection '{collection_name}' imported successfully!")
                            
                except Exception as e:
                    st.error(f"Error parsing CSV file: {e}")
        
        elif import_options == "Another ChromaDB":
            # Remote ChromaDB connection
            with st.form("remote_chroma_form"):
                st.markdown("### Remote ChromaDB Connection")
                
                remote_host = st.text_input("Host")
                remote_port = st.number_input("Port", value=8000)
                remote_ssl = st.checkbox("Use SSL")
                remote_api_key = st.text_input("API Key (if required)", type="password")
                
                st.markdown("### Collection Selection")
                collection_name = st.text_input("New Collection Name")
                source_collection = st.text_input("Source Collection Name")
                
                submit_button = st.form_submit_button("Import Collection")
                
                if submit_button:
                    # This would be implemented with actual import logic
                    st.success(f"Collection '{collection_name}' imported successfully!")
    
    with col2:
        # Export section
        st.markdown("### Export Collection")
        
        if not st.session_state.collections:
            st.info("No collections available for export")
            return
        
        export_collection = st.selectbox(
            "Select Collection to Export",
            options=[c.get("name") for c in st.session_state.collections]
        )
        
        export_format = st.radio(
            "Export Format",
            options=["JSON", "CSV", "JSONL"],
            horizontal=True
        )
        
        include_options = st.multiselect(
            "Include in Export",
            options=["Documents", "Embeddings", "Metadata", "IDs"],
            default=["Documents", "Metadata", "IDs"]
        )
        
        if st.button("Export Collection"):
            # This would be implemented with actual export logic
            st.success(f"Collection '{export_collection}' exported successfully!")
            
            # Add download button (placeholder)
            st.download_button(
                "Download Export File",
                data="Example export data",
                file_name=f"{export_collection}_export.{export_format.lower()}",
                mime="application/octet-stream"
            )