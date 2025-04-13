"""
Embedding models for ChromaLens.
"""

from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
import numpy as np


class Embedding(BaseModel):
    """Model for a single embedding vector."""
    
    vector: List[float] = Field(..., description="Embedding vector values")
    
    @validator('vector')
    def validate_vector(cls, v):
        """Validate vector format."""
        if not v:
            raise ValueError("Vector cannot be empty")
        return v
    
    def as_numpy(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array(self.vector, dtype=np.float32)
    
    @classmethod
    def from_numpy(cls, array: np.ndarray) -> 'Embedding':
        """Create from numpy array."""
        return cls(vector=array.tolist())
    
    class Config:
        """Pydantic config for Embedding model."""
        
        schema_extra = {
            "example": {
                "vector": [0.1, 0.2, 0.3, 0.4, 0.5]
            }
        }


class ItemBase(BaseModel):
    """Base model for collection items."""
    
    id: str = Field(..., description="Unique ID of the item")


class Item(ItemBase):
    """Model for a collection item with embedding."""
    
    embedding: Embedding = Field(..., description="The item's embedding vector")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Item metadata")
    document: Optional[str] = Field(None, description="Original document text")
    uri: Optional[str] = Field(None, description="URI reference")


class AddRequest(BaseModel):
    """Model for adding items to a collection."""
    
    ids: Optional[List[str]] = Field(None, description="IDs of the items (generated if not provided)")
    embeddings: List[List[float]] = Field(..., description="Embedding vectors")
    metadatas: Optional[List[Dict[str, Any]]] = Field(None, description="Optional metadata for each item")
    documents: Optional[List[str]] = Field(None, description="Optional document text for each item")
    uris: Optional[List[str]] = Field(None, description="Optional URIs for each item")
    
    @validator('embeddings')
    def validate_embeddings(cls, v):
        """Validate embeddings format."""
        if not v:
            raise ValueError("Embeddings list cannot be empty")
        
        # Ensure all embeddings have the same dimension
        dimensions = set(len(embedding) for embedding in v)
        if len(dimensions) > 1:
            raise ValueError(f"All embeddings must have the same dimension, found {dimensions}")
            
        return v
    
    @root_validator
    def validate_lengths(cls, values):
        """Validate that all provided lists have the same length."""
        embeddings = values.get('embeddings')
        if not embeddings:
            return values
            
        count = len(embeddings)
        
        # Check other fields if provided
        for field_name in ['ids', 'metadatas', 'documents', 'uris']:
            field_value = values.get(field_name)
            if field_value is not None and len(field_value) != count:
                raise ValueError(f"Length mismatch: {field_name} has {len(field_value)} items, but embeddings has {count}")
                
        return values


class UpdateRequest(BaseModel):
    """Model for updating items in a collection."""
    
    ids: List[str] = Field(..., description="IDs of the items to update")
    embeddings: Optional[List[List[float]]] = Field(None, description="New embedding vectors")
    metadatas: Optional[List[Dict[str, Any]]] = Field(None, description="New metadata for each item")
    documents: Optional[List[str]] = Field(None, description="New document text for each item")
    uris: Optional[List[str]] = Field(None, description="New URIs for each item")
    
    @root_validator
    def validate_update_fields(cls, values):
        """Validate that at least one update field is provided."""
        ids = values.get('ids')
        if not ids:
            raise ValueError("IDs list cannot be empty")
            
        # Check that at least one update field is provided
        if all(values.get(field) is None for field in ['embeddings', 'metadatas', 'documents', 'uris']):
            raise ValueError("At least one of embeddings, metadatas, documents, or uris must be provided")
            
        # Check lengths of provided fields match ids length
        count = len(ids)
        for field_name in ['embeddings', 'metadatas', 'documents', 'uris']:
            field_value = values.get(field_name)
            if field_value is not None and len(field_value) != count:
                raise ValueError(f"Length mismatch: {field_name} has {len(field_value)} items, but ids has {count}")
                
        return values


class UpsertRequest(BaseModel):
    """Model for upserting items in a collection."""
    
    ids: List[str] = Field(..., description="IDs of the items to upsert")
    embeddings: List[List[float]] = Field(..., description="Embedding vectors")
    metadatas: Optional[List[Dict[str, Any]]] = Field(None, description="Optional metadata for each item")