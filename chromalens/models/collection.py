"""
Collection models for ChromaLens.
"""

from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from uuid import UUID

class HNSWConfig(BaseModel):
    """HNSW configuration for collections."""
    
    space: str = Field("l2", description="Distance function (e.g., 'l2', 'cosine', 'ip')")
    ef_construction: int = Field(100, description="Size of the dynamic list for ef_construction")
    ef_search: int = Field(100, description="Size of the dynamic list for ef_search")
    num_threads: int = Field(4, description="Number of threads to use during indexing")
    M: int = Field(16, description="Number of bi-directional links created for every new element during construction")
    resize_factor: float = Field(1.2, description="Resize factor for the index")
    batch_size: int = Field(100, description="Batch size for indexing")
    sync_threshold: int = Field(1000, description="Sync threshold")
    _type: str = Field("HNSWConfigurationInternal", description="Configuration type")


class CollectionConfig(BaseModel):
    """Configuration for a collection."""
    
    hnsw_configuration: Optional[HNSWConfig] = Field(None, description="HNSW configuration settings")
    _type: str = Field("CollectionConfigurationInternal", description="Configuration type")


class CollectionCreate(BaseModel):
    """Model for creating a collection."""
    
    name: str = Field(..., description="Name of the collection")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the collection")
    get_or_create: bool = Field(False, description="If True, get existing collection if it exists")
    dimension: Optional[int] = Field(None, description="Dimensionality of the embeddings")
    configuration: Optional[CollectionConfig] = Field(None, description="Optional configuration for the collection")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        """Validate collection name format."""
        if not v or not v.strip():
            raise ValueError("Collection name cannot be empty")
        if len(v) > 64:
            raise ValueError("Collection name cannot exceed 64 characters")
        # Add additional validation rules if needed
        return v
    
    @validator('dimension')
    def dimension_must_be_positive(cls, v):
        """Validate dimension is positive."""
        if v is not None and v <= 0:
            raise ValueError("Dimension must be positive")
        return v


class Collection(BaseModel):
    """Model for a collection."""
    
    id: str = Field(..., description="Unique ID of the collection")
    name: str = Field(..., description="Name of the collection")
    tenant: str = Field(..., description="Tenant the collection belongs to")
    database: str = Field(..., description="Database the collection belongs to")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Collection metadata")
    dimension: int = Field(..., description="Dimensionality of the embeddings")
    configuration_json: CollectionConfig = Field(..., description="Collection configuration")
    version: int = Field(0, description="Collection version")
    
    class Config:
        """Pydantic config for Collection model."""
        
        schema_extra = {
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "name": "sample_collection",
                "tenant": "default_tenant",
                "database": "default_database",
                "metadata": None,
                "dimension": 768,
                "configuration_json": {
                    "hnsw_configuration": {
                        "space": "l2",
                        "ef_construction": 100,
                        "ef_search": 100,
                        "num_threads": 4,
                        "M": 16,
                        "resize_factor": 1.2,
                        "batch_size": 100,
                        "sync_threshold": 1000,
                        "_type": "HNSWConfigurationInternal"
                    },
                    "_type": "CollectionConfigurationInternal"
                },
                "version": 0
            }
        }


class CollectionsResponse(BaseModel):
    """Model for a list of collections response."""
    
    collections: List[Collection] = Field(..., description="List of collections")
    
    class Config:
        """Pydantic config for CollectionsResponse model."""
        
        schema_extra = {
            "example": {
                "collections": [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "name": "collection1",
                        "tenant": "default_tenant",
                        "database": "default_database",
                        "metadata": None,
                        "dimension": 768,
                        "configuration_json": {
                            "hnsw_configuration": {
                                "space": "l2",
                                "ef_construction": 100,
                                "ef_search": 100,
                                "num_threads": 4,
                                "M": 16,
                                "resize_factor": 1.2,
                                "batch_size": 100,
                                "sync_threshold": 1000,
                                "_type": "HNSWConfigurationInternal"
                            },
                            "_type": "CollectionConfigurationInternal"
                        },
                        "version": 0
                    }
                ]
            }
        }


class CollectionUpdateRequest(BaseModel):
    """Model for updating a collection."""
    
    new_name: Optional[str] = Field(None, description="New name for the collection")
    new_metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata for the collection")
    
    @validator('new_name')
    def name_must_be_valid(cls, v):
        """Validate collection name format."""
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Collection name cannot be empty")
        if len(v) > 64:
            raise ValueError("Collection name cannot exceed 64 characters")
        # Add additional validation rules if needed
        return v
    
    @root_validator
    def check_at_least_one_field(cls, values):
        """Validate that at least one field is provided."""
        if values.get('new_name') is None and values.get('new_metadata') is None:
            raise ValueError("At least one of new_name or new_metadata must be provided")
        return values


class CollectionCountResponse(BaseModel):
    """Model for a collection count response."""
    
    count: int = Field(..., description="Number of items in the collection")
    
    class Config:
        """Pydantic config for CollectionCountResponse model."""
        
        schema_extra = {
            "example": {
                "count": 100
            }
        }