"""
Utility functions for ChromaLens UI
"""

import streamlit as st
import pandas as pd
import json
import datetime
import re
from typing import Dict, List, Any, Union, Optional

def format_timestamp(timestamp: Union[int, float, str]) -> str:
    """Format a timestamp into a human-readable string"""
    if isinstance(timestamp, str):
        try:
            # Try to convert string to float (assuming it's a unix timestamp)
            timestamp = float(timestamp)
        except ValueError:
            # If it's already a formatted date string, return as is
            return timestamp
    
    # Convert to datetime and format
    if timestamp > 1e12:  # Microseconds
        dt = datetime.datetime.fromtimestamp(timestamp / 1e6)
    elif timestamp > 1e9:  # Nanoseconds
        dt = datetime.datetime.fromtimestamp(timestamp / 1e9)
    else:  # Seconds
        dt = datetime.datetime.fromtimestamp(timestamp)
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_json(json_data: Union[Dict, List, str], indent: int = 2) -> str:
    """Format JSON data with proper indentation"""
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            return json_data
    
    return json.dumps(json_data, indent=indent)

def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    
    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{size_kb:.2f} KB"
    
    size_mb = size_kb / 1024
    if size_mb < 1024:
        return f"{size_mb:.2f} MB"
    
    size_gb = size_mb / 1024
    return f"{size_gb:.2f} GB"

def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """Truncate text to a maximum length, optionally adding ellipsis"""
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    if add_ellipsis:
        truncated += "..."
    
    return truncated

def format_collection_info(collection: Dict[str, Any]) -> Dict[str, Any]:
    """Format collection information for display"""
    formatted = {}
    
    # Basic info
    formatted["name"] = collection.get("name", "")
    formatted["id"] = collection.get("id", "")
    
    # Dimension
    formatted["dimension"] = collection.get("dimension", 0)
    
    # Metadata
    metadata = collection.get("metadata", {})
    formatted["metadata"] = metadata
    
    # Embedding function info
    if metadata and "embedding_function" in metadata:
        embedding_fn = metadata["embedding_function"]
        formatted["embedding_function"] = f"{embedding_fn.get('type', 'unknown')} ({embedding_fn.get('model', 'unknown')})"
    else:
        formatted["embedding_function"] = "None"
    
    return formatted

def create_dataframe_from_items(items: Dict[str, Any]) -> pd.DataFrame:
    """Create a DataFrame from ChromaDB items response"""
    if not items:
        return pd.DataFrame()
    
    # Extract components
    ids = items.get("ids", [])
    documents = items.get("documents", [])
    metadatas = items.get("metadatas", [])
    embeddings = items.get("embeddings", [])
    
    # Create DataFrame data
    data = []
    for i in range(len(ids)):
        item = {"id": ids[i]}
        
        # Add document if available
        if i < len(documents) and documents:
            item["document"] = truncate_text(documents[i], 100) if documents[i] else None
        
        # Add metadata if available
        if i < len(metadatas) and metadatas:
            item["metadata"] = json.dumps(metadatas[i]) if metadatas[i] else None
        
        # Add embedding dimension if available
        if i < len(embeddings) and embeddings:
            item["embedding_dim"] = len(embeddings[i]) if embeddings[i] else None
        
        data.append(item)
    
    return pd.DataFrame(data)

def parse_vector_from_string(vector_string: str) -> List[float]:
    """Parse a vector from string input (JSON array or comma-separated values)"""
    vector_string = vector_string.strip()
    
    # Try to parse as JSON array
    if vector_string.startswith('[') and vector_string.endswith(']'):
        try:
            return json.loads(vector_string)
        except json.JSONDecodeError:
            pass
    
    # Try to parse as comma-separated values
    values = []
    for value in vector_string.split(','):
        value = value.strip()
        if value:
            try:
                values.append(float(value))
            except ValueError:
                raise ValueError(f"Invalid vector value: {value}")
    
    return values

def render_metric_card(title: str, value: Any, delta: Optional[Any] = None, help_text: Optional[str] = None):
    """Render a styled metric card with title, value, and optional delta"""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-delta">{delta}</div>' if delta is not None else ''}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if help_text:
        st.caption(help_text)

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)}m {int(seconds % 60)}s"
    
    hours = minutes / 60
    return f"{int(hours)}h {int(minutes % 60)}m"

def parse_metadata_filter(filter_string: str) -> Dict[str, Any]:
    """Parse metadata filter string to ChromaDB query format"""
    if not filter_string:
        return {}
    
    try:
        # Try to parse as JSON
        return json.loads(filter_string)
    except json.JSONDecodeError:
        raise ValueError("Invalid filter format. Must be valid JSON.")

def check_embedding_dimension(vector: List[float], expected_dim: int) -> bool:
    """Check if a vector has the expected dimension"""
    return len(vector) == expected_dim