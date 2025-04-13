"""
Formatting utilities for ChromaLens.

This module provides functions for formatting data in user-friendly ways.
"""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import textwrap


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as a pretty-printed JSON string.
    
    Args:
        data: Data to format
        indent: Number of spaces for indentation
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def format_timestamp(timestamp: Optional[int] = None) -> str:
    """
    Format a timestamp as a human-readable date string.
    
    Args:
        timestamp: Unix timestamp in seconds or None for current time
        
    Returns:
        Formatted date string
    """
    if timestamp is None:
        dt = datetime.now()
    else:
        # Handle timestamps in milliseconds or nanoseconds
        if timestamp > 1e12:  # Nanoseconds
            timestamp = timestamp / 1e9
        elif timestamp > 1e9:  # Milliseconds
            timestamp = timestamp / 1e3
            
        dt = datetime.fromtimestamp(timestamp)
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes as a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.23 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds as a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {int(remaining_seconds)}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


def format_list(items: List[Any], max_items: int = 10) -> str:
    """
    Format a list as a string, truncating if necessary.
    
    Args:
        items: List to format
        max_items: Maximum number of items to include
        
    Returns:
        Formatted list string
    """
    if not items:
        return "[]"
    
    if len(items) <= max_items:
        return str(items)
    
    truncated = items[:max_items]
    return f"{truncated} ... ({len(items) - max_items} more)"


def format_metadata(metadata: Dict[str, Any], max_depth: int = 2, current_depth: int = 0) -> str:
    """
    Format metadata as a human-readable string.
    
    Args:
        metadata: Metadata dictionary
        max_depth: Maximum depth to descend into nested dictionaries
        current_depth: Current depth (used for recursion)
        
    Returns:
        Formatted metadata string
    """
    if not metadata:
        return "{}"
    
    if current_depth >= max_depth:
        return "{...}"
    
    lines = []
    for key, value in metadata.items():
        if isinstance(value, dict):
            formatted_value = format_metadata(value, max_depth, current_depth + 1)
        elif isinstance(value, list) and len(value) > 5:
            formatted_value = format_list(value)
        else:
            formatted_value = str(value)
            
        lines.append(f"  {key}: {formatted_value}")
    
    return "{\n" + "\n".join(lines) + "\n}"


def format_document(document: str, max_length: int = 100) -> str:
    """
    Format a document string, truncating if necessary.
    
    Args:
        document: Document string
        max_length: Maximum length of the formatted string
        
    Returns:
        Formatted document string
    """
    if not document:
        return ""
    
    if len(document) <= max_length:
        return document
    
    return document[:max_length] + "..."


def format_collection_info(collection: Dict[str, Any]) -> str:
    """
    Format collection information as a human-readable string.
    
    Args:
        collection: Collection dictionary
        
    Returns:
        Formatted collection info string
    """
    lines = [
        f"Collection: {collection.get('name', 'Unnamed')}",
        f"ID: {collection.get('id', 'Unknown')}",
        f"Dimension: {collection.get('dimension', 'Unknown')}",
    ]
    
    if 'metadata' in collection and collection['metadata']:
        lines.append("Metadata:")
        metadata = collection['metadata']
        for key, value in metadata.items():
            lines.append(f"  {key}: {value}")
    
    return "\n".join(lines)


def format_table(data: List[Dict[str, Any]], columns: Optional[List[str]] = None, max_width: int = 120) -> str:
    """
    Format a list of dictionaries as a table.
    
    Args:
        data: List of dictionaries to format
        columns: List of columns to include (if None, use all keys from the first dict)
        max_width: Maximum width of each column
        
    Returns:
        Formatted table string
    """
    if not data:
        return "No data to display"
    
    # Determine columns to display
    if columns is None:
        columns = list(data[0].keys())
    
    # Calculate column widths
    col_widths = {col: len(col) for col in columns}
    for row in data:
        for col in columns:
            if col in row:
                col_widths[col] = max(col_widths[col], min(len(str(row[col])), max_width))
    
    # Create header row
    header = " | ".join(f"{col:{col_widths[col]}s}" for col in columns)
    separator = "-" * len(header)
    
    # Create data rows
    rows = []
    for row in data:
        formatted_row = []
        for col in columns:
            value = row.get(col, "")
            str_value = str(value)
            if len(str_value) > max_width:
                str_value = str_value[:max_width-3] + "..."
            formatted_row.append(f"{str_value:{col_widths[col]}s}")
        rows.append(" | ".join(formatted_row))
    
    # Combine all parts
    return "\n".join([header, separator] + rows)


def format_query_results(results: Dict[str, Any], max_results: int = 5) -> str:
    """
    Format query results as a human-readable string.
    
    Args:
        results: Query results dictionary
        max_results: Maximum number of results to include
        
    Returns:
        Formatted query results string
    """
    if not results or 'ids' not in results:
        return "No results"
    
    ids = results.get('ids', [])
    distances = results.get('distances', [])
    metadatas = results.get('metadatas', [])
    documents = results.get('documents', [])
    
    if not ids or not ids[0]:
        return "No matching results found"
    
    # Handle multiple queries
    query_count = len(ids)
    lines = []
    
    for q_idx in range(query_count):
        q_ids = ids[q_idx]
        result_count = len(q_ids)
        
        if query_count > 1:
            lines.append(f"\nQuery {q_idx+1} Results:")
        
        # Truncate results if needed
        if result_count > max_results:
            lines.append(f"Showing top {max_results} of {result_count} results:")
            q_ids = q_ids[:max_results]
        else:
            lines.append(f"Found {result_count} results:")
        
        # Display each result
        for i, item_id in enumerate(q_ids):
            lines.append(f"\nResult {i+1}:")
            lines.append(f"  ID: {item_id}")
            
            if distances and len(distances) > q_idx and len(distances[q_idx]) > i:
                lines.append(f"  Distance: {distances[q_idx][i]:.6f}")
            
            if metadatas and len(metadatas) > q_idx and len(metadatas[q_idx]) > i:
                md = metadatas[q_idx][i]
                if md:
                    lines.append("  Metadata:")
                    for k, v in md.items():
                        lines.append(f"    {k}: {v}")
            
            if documents and len(documents) > q_idx and len(documents[q_idx]) > i:
                doc = documents[q_idx][i]
                if doc:
                    lines.append("  Document:")
                    doc_preview = textwrap.shorten(doc, width=80, placeholder="...")
                    lines.append(f"    {doc_preview}")
    
    return "\n".join(lines)