"""
Query models for ChromaLens.
"""

from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field, validator, root_validator


class WhereFilter(BaseModel):
    """Base model for where filter conditions."""
    
    class Config:
        """Pydantic config for WhereFilter model."""
        
        extra = "allow"  # Allow additional fields


class GetRequest(BaseModel):
    """Model for retrieving items from a collection."""
    
    ids: Optional[List[str]] = Field(None, description="IDs of the items to retrieve")
    where: Optional[Dict[str, Any]] = Field(None, description="Filter conditions on metadata")
    where_document: Optional[Dict[str, Any]] = Field(None, description="Filter conditions on documents")
    limit: Optional[int] = Field(None, description="Maximum number of results to return")
    offset: Optional[int] = Field(None, description="Offset for pagination")
    include: Optional[List[str]] = Field(None, description="Fields to include in the response")
    
    @validator('limit')
    def validate_limit(cls, v):
        """Validate limit is positive."""
        if v is not None and v <= 0:
            raise ValueError("Limit must be positive")
        return v
    
    @validator('offset')
    def validate_offset(cls, v):
        """Validate offset is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Offset cannot be negative")
        return v
    
    @validator('include')
    def validate_include(cls, v):
        """Validate include fields."""
        if v is not None:
            valid_include = {'metadatas', 'documents', 'embeddings', 'uris'}
            for field in v:
                if field not in valid_include:
                    raise ValueError(f"Invalid include field: {field}. Valid fields are: {valid_include}")
        return v
    
    @root_validator
    def validate_at_least_one_filter(cls, values):
        """Validate that at least one filter is provided."""
        if values.get('ids') is None and values.get('where') is None and values.get('where_document') is None:
            # It's valid to have no filters, which means "get everything"
            pass
        return values


class DeleteRequest(BaseModel):
    """Model for deleting items from a collection."""
    
    ids: Optional[List[str]] = Field(None, description="IDs of the items to delete")
    where: Optional[Dict[str, Any]] = Field(None, description="Filter conditions on metadata")
    where_document: Optional[Dict[str, Any]] = Field(None, description="Filter conditions on documents")
    
    @root_validator
    def validate_at_least_one_filter(cls, values):
        """Validate that at least one filter is provided."""
        if values.get('ids') is None and values.get('where') is None and values.get('where_document') is None:
            raise ValueError("At least one of ids, where, or where_document must be provided")
        return values


class QueryRequest(BaseModel):
    """Model for querying a collection."""
    
    query_embeddings: List[List[float]] = Field(..., description="Query embedding vectors")
    n_results: int = Field(10, description="Number of results to return per query")
    where: Optional[Dict[str, Any]] = Field(None, description="Filter conditions on metadata")
    where_document: Optional[Dict[str, Any]] = Field(None, description="Filter conditions on documents")
    include: Optional[List[str]] = Field(None, description="Fields to include in the response")
    
    @validator('query_embeddings')
    def validate_query_embeddings(cls, v):
        """Validate query embeddings format."""
        if not v:
            raise ValueError("Query embeddings list cannot be empty")
        
        # Ensure all embeddings have the same dimension
        dimensions = set(len(embedding) for embedding in v)
        if len(dimensions) > 1:
            raise ValueError(f"All query embeddings must have the same dimension, found {dimensions}")
            
        return v
    
    @validator('n_results')
    def validate_n_results(cls, v):
        """Validate n_results is positive."""
        if v <= 0:
            raise ValueError("n_results must be positive")
        return v
    
    @validator('include')
    def validate_include(cls, v):
        """Validate include fields."""
        if v is not None:
            valid_include = {'metadatas', 'documents', 'distances', 'embeddings', 'uris'}
            for field in v:
                if field not in valid_include:
                    raise ValueError(f"Invalid include field: {field}. Valid fields are: {valid_include}")
        return v


class QueryResult(BaseModel):
    """Model for a single query result."""
    
    id: str = Field(..., description="ID of the item")
    distance: Optional[float] = Field(None, description="Distance to the query embedding")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Item metadata")
    document: Optional[str] = Field(None, description="Original document text")
    embedding: Optional[List[float]] = Field(None, description="Embedding vector")
    uri: Optional[str] = Field(None, description="URI reference")


class QueryResponse(BaseModel):
    """Model for a query response."""
    
    ids: List[List[str]] = Field(..., description="IDs for each query result")
    distances: Optional[List[List[float]]] = Field(None, description="Distances for each query result")
    metadatas: Optional[List[List[Dict[str, Any]]]] = Field(None, description="Metadata for each query result")
    documents: Optional[List[List[str]]] = Field(None, description="Documents for each query result")
    embeddings: Optional[List[List[List[float]]]] = Field(None, description="Embeddings for each query result")
    uris: Optional[List[List[str]]] = Field(None, description="URIs for each query result")
    
    def get_results(self, query_idx: int = 0) -> List[QueryResult]:
        """
        Get structured results for a specific query.
        
        Args:
            query_idx: Index of the query to get results for (default: 0)
            
        Returns:
            List of QueryResult objects
        """
        if query_idx >= len(self.ids):
            raise IndexError(f"Query index {query_idx} out of range (0-{len(self.ids)-1})")
            
        results = []
        
        for i, item_id in enumerate(self.ids[query_idx]):
            result = QueryResult(id=item_id)
            
            # Add optional fields if available
            if self.distances is not None:
                result.distance = self.distances[query_idx][i]
                
            if self.metadatas is not None:
                result.metadata = self.metadatas[query_idx][i]
                
            if self.documents is not None:
                result.document = self.documents[query_idx][i]
                
            if self.embeddings is not None:
                result.embedding = self.embeddings[query_idx][i]
                
            if self.uris is not None:
                result.uri = self.uris[query_idx][i]
                
            results.append(result)
            
        return results