"""
Validation utilities for ChromaLens.

This module provides functions for validating inputs before making API calls.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Union, Tuple


def validate_not_empty(value: Any, name: str) -> Any:
    """
    Validate that a value is not None or empty.
    
    Args:
        value: Value to validate
        name: Name of the value for the error message
        
    Returns:
        The original value if valid
        
    Raises:
        ValueError: If the value is None or empty
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    
    if isinstance(value, (str, list, dict, set, tuple)) and len(value) == 0:
        raise ValueError(f"{name} cannot be empty")
    
    return value


def validate_uuid(value: str, name: str) -> str:
    """
    Validate that a string is a valid UUID.
    
    Args:
        value: String to validate
        name: Name of the value for the error message
        
    Returns:
        The original string if valid
        
    Raises:
        ValueError: If the string is not a valid UUID
    """
    try:
        uuid_obj = uuid.UUID(value)
        return str(uuid_obj)
    except (ValueError, AttributeError, TypeError):
        raise ValueError(f"{name} must be a valid UUID")


def validate_name(value: str, name: str, max_length: int = 64) -> str:
    """
    Validate a name string.
    
    Args:
        value: String to validate
        name: Name of the value for the error message
        max_length: Maximum allowed length for the name
        
    Returns:
        The original string if valid
        
    Raises:
        ValueError: If the string is invalid
    """
    # Check if the value is not empty
    validate_not_empty(value, name)
    
    # Check if the value is a string
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    
    # Check if the value is too long
    if len(value) > max_length:
        raise ValueError(f"{name} cannot exceed {max_length} characters")
    
    # Check if the value contains only allowed characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValueError(f"{name} can only contain letters, numbers, underscores, and hyphens")
    
    return value


def validate_embeddings(embeddings: List[List[float]], name: str = "embeddings", dimension: Optional[int] = None) -> List[List[float]]:
    """
    Validate a list of embedding vectors.
    
    Args:
        embeddings: List of embedding vectors to validate
        name: Name of the value for the error message
        dimension: Optional expected dimension for the embeddings
        
    Returns:
        The original embeddings if valid
        
    Raises:
        ValueError: If the embeddings are invalid
    """
    # Check if the embeddings are not empty
    validate_not_empty(embeddings, name)
    
    # Check if the embeddings are a list
    if not isinstance(embeddings, list):
        raise ValueError(f"{name} must be a list")
    
    # Check if the embeddings are a list of lists
    if not all(isinstance(emb, list) for emb in embeddings):
        raise ValueError(f"{name} must be a list of lists")
    
    # Check if the embeddings are a list of lists of floats
    for i, emb in enumerate(embeddings):
        if not all(isinstance(val, (int, float)) for val in emb):
            raise ValueError(f"{name}[{i}] must contain only numeric values")
    
    # Check if all embeddings have the same dimension
    dimensions = set(len(emb) for emb in embeddings)
    if len(dimensions) > 1:
        raise ValueError(f"{name} must all have the same dimension, found dimensions: {dimensions}")
    
    # Check if the embeddings have the expected dimension
    if dimension is not None:
        actual_dimension = next(iter(dimensions)) if dimensions else 0
        if actual_dimension != dimension:
            raise ValueError(f"{name} must have dimension {dimension}, found {actual_dimension}")
    
    return embeddings


def validate_ids(ids: List[str], name: str = "ids") -> List[str]:
    """
    Validate a list of IDs.
    
    Args:
        ids: List of IDs to validate
        name: Name of the value for the error message
        
    Returns:
        The original IDs if valid
        
    Raises:
        ValueError: If the IDs are invalid
    """
    # Check if the IDs are not empty
    validate_not_empty(ids, name)
    
    # Check if the IDs are a list
    if not isinstance(ids, list):
        raise ValueError(f"{name} must be a list")
    
    # Check if the IDs are a list of strings
    if not all(isinstance(id_, str) for id_ in ids):
        raise ValueError(f"{name} must contain only strings")
    
    # Check if the IDs are unique
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name} must contain unique values")
    
    return ids


def validate_lists_same_length(*lists_with_names: Tuple[List[Any], str]) -> None:
    """
    Validate that multiple lists have the same length.
    
    Args:
        *lists_with_names: Tuples of (list, name) to validate
        
    Raises:
        ValueError: If the lists have different lengths
    """
    # Filter out None values
    non_none_lists = [(lst, name) for lst, name in lists_with_names if lst is not None]
    
    if len(non_none_lists) <= 1:
        return
    
    # Get the length of the first list
    first_list, first_name = non_none_lists[0]
    expected_length = len(first_list)
    
    # Check if all other lists have the same length
    for lst, name in non_none_lists[1:]:
        if len(lst) != expected_length:
            raise ValueError(f"{name} has length {len(lst)}, but {first_name} has length {expected_length}")


def validate_metadata(metadata: Union[Dict[str, Any], List[Dict[str, Any]]], name: str = "metadata") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Validate metadata dictionaries or list of dictionaries.
    
    Args:
        metadata: Metadata to validate
        name: Name of the value for the error message
        
    Returns:
        The original metadata if valid
        
    Raises:
        ValueError: If the metadata is invalid
    """
    # Check if the metadata is not None (empty dict is allowed)
    if metadata is None:
        raise ValueError(f"{name} cannot be None")
    
    # Handle single dictionary case
    if isinstance(metadata, dict):
        # Validate keys are strings
        if not all(isinstance(k, str) for k in metadata.keys()):
            raise ValueError(f"All keys in {name} must be strings")
        return metadata
    
    # Handle list of dictionaries case
    if isinstance(metadata, list):
        if not all(isinstance(m, dict) for m in metadata):
            raise ValueError(f"{name} must be a list of dictionaries")
        
        # Validate keys in all dictionaries are strings
        for i, m in enumerate(metadata):
            if not all(isinstance(k, str) for k in m.keys()):
                raise ValueError(f"All keys in {name}[{i}] must be strings")
        
        return metadata
    
    raise ValueError(f"{name} must be a dictionary or list of dictionaries")


def validate_documents(documents: List[str], name: str = "documents") -> List[str]:
    """
    Validate a list of document strings.
    
    Args:
        documents: List of document strings to validate
        name: Name of the value for the error message
        
    Returns:
        The original documents if valid
        
    Raises:
        ValueError: If the documents are invalid
    """
    # Check if the documents are not empty
    validate_not_empty(documents, name)
    
    # Check if the documents are a list
    if not isinstance(documents, list):
        raise ValueError(f"{name} must be a list")
    
    # Check if the documents are a list of strings
    if not all(isinstance(doc, str) for doc in documents):
        raise ValueError(f"{name} must contain only strings")
    
    return documents


def validate_where_clause(where: Dict[str, Any], name: str = "where") -> Dict[str, Any]:
    """
    Validate a where clause for filtering.
    
    Args:
        where: Where clause to validate
        name: Name of the value for the error message
        
    Returns:
        The original where clause if valid
        
    Raises:
        ValueError: If the where clause is invalid
    """
    if not isinstance(where, dict):
        raise ValueError(f"{name} must be a dictionary")
    
    # Check for logical operators
    logical_operators = ["$and", "$or", "$not"]
    for op in logical_operators:
        if op in where:
            if op in ["$and", "$or"]:
                if not isinstance(where[op], list):
                    raise ValueError(f"{name}.{op} must be a list")
                
                # Recursively validate each condition in the list
                for i, condition in enumerate(where[op]):
                    validate_where_clause(condition, f"{name}.{op}[{i}]")
            
            elif op == "$not":
                if not isinstance(where[op], dict):
                    raise ValueError(f"{name}.{op} must be a dictionary")
                
                # Recursively validate the negated condition
                validate_where_clause(where[op], f"{name}.{op}")
    
    # Check for field conditions (anything not a logical operator)
    for field, condition in where.items():
        if field not in logical_operators:
            if isinstance(condition, dict):
                # Validate operators
                for op, value in condition.items():
                    if not op.startswith("$"):
                        raise ValueError(f"Invalid operator {op} in {name}.{field}")
    
    return where