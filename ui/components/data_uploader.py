"""
Data uploader components for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import json
import uuid
import re
from io import StringIO

from components.header import show_success, show_error, show_info, show_warning

def render_data_uploader():
    """Render the data uploader interface"""
    if not st.session_state.collections:
        show_warning("No collections available. Please create a collection first.")
        return
    
    # Collection selection
    collection_names = [c.get("name") for c in st.session_state.collections]
    selected_collection = st.selectbox(
        "Select Collection", 
        options=collection_names,
        key="uploader_collection_select"
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
    
    # Upload tabs
    upload_tabs = st.tabs(["Text Upload", "CSV Upload", "Batch Upload"])
    
    # Text Upload Tab
    with upload_tabs[0]:
        render_text_upload(selected_collection, collection)
    
    # CSV Upload Tab
    with upload_tabs[1]:
        render_csv_upload(selected_collection, collection)
    
    # Batch Upload Tab
    with upload_tabs[2]:
        render_batch_upload(selected_collection, collection)

def render_text_upload(collection_name, collection):
    """Render text upload interface"""
    st.subheader("Upload Text Documents")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        documents = st.text_area(
            "Enter text documents (one per line or paragraph)", 
            height=200,
            help="Each line or paragraph will be treated as a separate document"
        )
        
        # Option to split documents
        split_strategy = st.radio(
            "Document splitting strategy",
            options=["One document per line", "Split by paragraphs", "No splitting (single document)"],
            horizontal=True
        )
    
    with col2:
        # Metadata options
        st.markdown("### Metadata")
        
        # Common metadata for all documents
        common_metadata = st.text_area(
            "Common metadata (JSON)",
            help="This metadata will be applied to all documents",
            placeholder='{"source": "manual", "category": "notes"}'
        )
        
        # ID generation
        id_generation = st.radio(
            "ID Generation",
            options=["Auto-generate UUIDs", "Use document hash", "Sequential numbers"],
            horizontal=True
        )
    
    # Submit button
    if st.button("Upload Documents", key="upload_text_documents"):
        if not documents:
            show_warning("Please enter some text to upload")
            return
        
        # Process documents based on split strategy
        if split_strategy == "One document per line":
            document_list = [doc.strip() for doc in documents.split('\n') if doc.strip()]
        elif split_strategy == "Split by paragraphs":
            document_list = [doc.strip() for doc in re.split(r'\n\s*\n', documents) if doc.strip()]
        else:
            document_list = [documents]
        
        # Generate IDs
        if id_generation == "Auto-generate UUIDs":
            ids = [str(uuid.uuid4()) for _ in document_list]
        elif id_generation == "Use document hash":
            ids = [str(hash(doc)) for doc in document_list]
        else:
            ids = [f"doc_{i+1}" for i in range(len(document_list))]
        
        # Process common metadata
        metadata_list = []
        if common_metadata:
            try:
                common_metadata_dict = json.loads(common_metadata)
                metadata_list = [common_metadata_dict.copy() for _ in document_list]
            except json.JSONDecodeError:
                show_error("Invalid JSON in common metadata")
                return
        else:
            metadata_list = [{"source": "ui_upload"} for _ in document_list]
        
        # Show a spinner while processing
        with st.spinner(f"Uploading {len(document_list)} documents..."):
            try:
                # Upload documents
                response = st.session_state.client.add_documents(
                    collection_name=collection_name,
                    documents=document_list,
                    metadatas=metadata_list,
                    ids=ids,
                    database=st.session_state.connection_params['database'],
                    tenant=st.session_state.connection_params['tenant']
                )
                
                show_success(f"Successfully uploaded {len(document_list)} documents!")
                
                # Show document preview
                with st.expander("Document Preview", expanded=True):
                    preview_df = pd.DataFrame({
                        "ID": ids[:5],
                        "Document": [doc[:100] + "..." if len(doc) > 100 else doc for doc in document_list[:5]],
                        "Metadata": [json.dumps(meta) for meta in metadata_list[:5]]
                    })
                    st.dataframe(preview_df, use_container_width=True)
                    
                    if len(document_list) > 5:
                        st.caption(f"Showing 5 of {len(document_list)} documents")
                
            except Exception as e:
                show_error(f"Failed to upload documents: {e}")

def render_csv_upload(collection_name, collection):
    """Render CSV upload interface"""
    st.subheader("Upload from CSV")
    
    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
    
    if uploaded_file is not None:
        # Read CSV content
        csv_content = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(StringIO(csv_content))
        
        # Display preview
        st.write("CSV Preview:")
        st.dataframe(df.head(5), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Column mapping
            st.markdown("### Column Mapping")
            
            # Document column
            document_column = st.selectbox(
                "Document Column", 
                options=df.columns,
                key="csv_document_column"
            )
            
            # ID column
            id_columns = ["[Auto-generate]"] + list(df.columns)
            id_column = st.selectbox(
                "ID Column",
                options=id_columns,
                key="csv_id_column"
            )
            
            # Metadata columns
            st.markdown("### Metadata Columns")
            metadata_columns = st.multiselect(
                "Select columns to include as metadata",
                options=[col for col in df.columns if col != document_column],
                key="csv_metadata_columns"
            )
        
        with col2:
            # Upload options
            st.markdown("### Upload Options")
            
            chunk_size = st.number_input(
                "Chunk Size",
                min_value=1,
                max_value=1000,
                value=100,
                help="Number of documents to upload in each batch"
            )
            
            # Skip empty rows
            skip_empty = st.checkbox("Skip empty document cells", value=True)
        
        # Submit button
        if st.button("Upload CSV Data", key="upload_csv_data"):
            if document_column not in df.columns:
                show_error("Please select a valid document column")
                return
            
            # Process the DataFrame
            # Filter out empty document cells if requested
            if skip_empty:
                df = df.dropna(subset=[document_column])
            
            # Process documents
            documents = df[document_column].tolist()
            
            # Process IDs
            if id_column == "[Auto-generate]":
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            else:
                ids = df[id_column].astype(str).tolist()
            
            # Process metadata
            metadata_list = []
            if metadata_columns:
                for _, row in df.iterrows():
                    metadata = {}
                    for col in metadata_columns:
                        # Handle NaN values
                        if pd.isna(row[col]):
                            continue
                        metadata[col] = row[col]
                    metadata_list.append(metadata)
            else:
                metadata_list = [{"source": "csv_upload"} for _ in documents]
            
            # Show a spinner while processing
            with st.spinner(f"Uploading {len(documents)} documents in chunks of {chunk_size}..."):
                try:
                    # Upload in chunks
                    total_uploaded = 0
                    progress_bar = st.progress(0)
                    
                    for i in range(0, len(documents), chunk_size):
                        chunk_docs = documents[i:i+chunk_size]
                        chunk_ids = ids[i:i+chunk_size]
                        chunk_metadata = metadata_list[i:i+chunk_size]
                        
                        response = st.session_state.client.add_documents(
                            collection_name=collection_name,
                            documents=chunk_docs,
                            metadatas=chunk_metadata,
                            ids=chunk_ids,
                            database=st.session_state.connection_params['database'],
                            tenant=st.session_state.connection_params['tenant']
                        )
                        
                        total_uploaded += len(chunk_docs)
                        progress_bar.progress(total_uploaded / len(documents))
                    
                    show_success(f"Successfully uploaded {total_uploaded} documents from CSV!")
                    
                except Exception as e:
                    show_error(f"Failed to upload documents: {e}")

def render_batch_upload(collection_name, collection):
    """Render batch upload interface"""
    st.subheader("Batch Document Upload")
    
    # Text area for document input
    documents_json = st.text_area(
        "Enter documents in JSON format",
        height=300,
        help="Format: [{\"id\": \"doc1\", \"document\": \"text\", \"metadata\": {\"key\": \"value\"}}]",
        placeholder='[\n  {\n    "id": "doc1",\n    "document": "This is document 1",\n    "metadata": {"source": "batch", "category": "example"}\n  },\n  {\n    "id": "doc2",\n    "document": "This is document 2",\n    "metadata": {"source": "batch", "category": "example"}\n  }\n]'
    )
    
    # Upload options
    col1, col2 = st.columns(2)
    
    with col1:
        auto_ids = st.checkbox("Auto-generate missing IDs", value=True)
        default_metadata = st.text_input(
            "Default metadata for documents without metadata (JSON)",
            placeholder='{"source": "batch_upload"}'
        )
    
    # Submit button
    if st.button("Upload Batch Documents", key="upload_batch_documents"):
        if not documents_json:
            show_warning("Please enter document data in JSON format")
            return
        
        try:
            # Parse JSON data
            documents_data = json.loads(documents_json)
            
            if not isinstance(documents_data, list):
                show_error("JSON data must be a list of document objects")
                return
            
            # Extract document components
            ids = []
            documents = []
            metadatas = []
            
            # Parse default metadata
            default_meta = {"source": "batch_upload"}
            if default_metadata:
                try:
                    default_meta = json.loads(default_metadata)
                except json.JSONDecodeError:
                    show_error("Invalid JSON in default metadata")
                    return
            
            for i, doc_obj in enumerate(documents_data):
                # Check document format
                if not isinstance(doc_obj, dict):
                    show_error(f"Item {i} is not a valid document object")
                    return
                
                # Extract document
                if "document" not in doc_obj:
                    show_error(f"Item {i} is missing the 'document' field")
                    return
                documents.append(doc_obj["document"])
                
                # Extract ID
                if "id" in doc_obj:
                    ids.append(doc_obj["id"])
                elif auto_ids:
                    ids.append(str(uuid.uuid4()))
                else:
                    show_error(f"Item {i} is missing the 'id' field and auto-generation is disabled")
                    return
                
                # Extract metadata
                if "metadata" in doc_obj and isinstance(doc_obj["metadata"], dict):
                    metadatas.append(doc_obj["metadata"])
                else:
                    metadatas.append(default_meta.copy())
            
            # Upload documents
            with st.spinner(f"Uploading {len(documents)} documents..."):
                try:
                    response = st.session_state.client.add_documents(
                        collection_name=collection_name,
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids,
                        database=st.session_state.connection_params['database'],
                        tenant=st.session_state.connection_params['tenant']
                    )
                    
                    show_success(f"Successfully uploaded {len(documents)} documents!")
                    
                except Exception as e:
                    show_error(f"Failed to upload documents: {e}")
            
        except json.JSONDecodeError:
            show_error("Invalid JSON format")
            return