"""
Metadata models for ChromaLens.
"""

from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator


class MetadataValue(BaseModel):
    """Base model for metadata values."""
    
    class Config:
        """Pydantic config for MetadataValue model."""
        
        extra = "allow"  # Allow any additional fields


class MetadataFilter(BaseModel):
    """Base model for metadata filters."""
    
    class Config:
        """Pydantic config for MetadataFilter model."""
        
        extra = "allow"  # Allow any additional fields


class TextFilter(BaseModel):
    """Filter for text fields."""
    
    contains: Optional[str] = Field(None, alias="$contains", description="Text contains this substring")
    starts_with: Optional[str] = Field(None, alias="$startsWith", description="Text starts with this substring")
    ends_with: Optional[str] = Field(None, alias="$endsWith", description="Text ends with this substring")
    eq: Optional[str] = Field(None, alias="$eq", description="Text equals this value")
    ne: Optional[str] = Field(None, alias="$ne", description="Text does not equal this value")
    in_list: Optional[List[str]] = Field(None, alias="$in", description="Text is in this list")
    not_in_list: Optional[List[str]] = Field(None, alias="$nin", description="Text is not in this list")
    
    class Config:
        """Pydantic config for TextFilter model."""
        
        extra = "allow"  # Allow any additional fields
        allow_population_by_field_name = True


class NumericFilter(BaseModel):
    """Filter for numeric fields."""
    
    eq: Optional[float] = Field(None, alias="$eq", description="Equals this value")
    ne: Optional[float] = Field(None, alias="$ne", description="Does not equal this value")
    gt: Optional[float] = Field(None, alias="$gt", description="Greater than this value")
    gte: Optional[float] = Field(None, alias="$gte", description="Greater than or equal to this value")
    lt: Optional[float] = Field(None, alias="$lt", description="Less than this value")
    lte: Optional[float] = Field(None, alias="$lte", description="Less than or equal to this value")
    in_list: Optional[List[float]] = Field(None, alias="$in", description="In this list of values")
    not_in_list: Optional[List[float]] = Field(None, alias="$nin", description="Not in this list of values")
    
    class Config:
        """Pydantic config for NumericFilter model."""
        
        extra = "allow"  # Allow any additional fields
        allow_population_by_field_name = True


class DateFilter(BaseModel):
    """Filter for date fields."""
    
    eq: Optional[str] = Field(None, alias="$eq", description="Equals this date")
    ne: Optional[str] = Field(None, alias="$ne", description="Does not equal this date")
    gt: Optional[str] = Field(None, alias="$gt", description="Greater than this date")
    gte: Optional[str] = Field(None, alias="$gte", description="Greater than or equal to this date")
    lt: Optional[str] = Field(None, alias="$lt", description="Less than this date")
    lte: Optional[str] = Field(None, alias="$lte", description="Less than or equal to this date")
    
    @validator('eq', 'ne', 'gt', 'gte', 'lt', 'lte')
    def validate_date(cls, v):
        """Validate date string format."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(f"Invalid date format: {v}. Use ISO format (e.g., '2023-01-01T00:00:00Z')")
        return v
    
    class Config:
        """Pydantic config for DateFilter model."""
        
        extra = "allow"  # Allow any additional fields
        allow_population_by_field_name = True


class LogicalOperator(BaseModel):
    """Logical operators for combining filters."""
    
    and_operator: Optional[List[Dict[str, Any]]] = Field(None, alias="$and", description="AND operator")
    or_operator: Optional[List[Dict[str, Any]]] = Field(None, alias="$or", description="OR operator")
    not_operator: Optional[Dict[str, Any]] = Field(None, alias="$not", description="NOT operator")
    
    @root_validator
    def validate_logical_operator(cls, values):
        """Validate that only one logical operator is used."""
        operators = [op for op in ['and_operator', 'or_operator', 'not_operator'] if values.get(op) is not None]
        if len(operators) > 1:
            raise ValueError(f"Only one logical operator can be used at a time, found: {operators}")
        return values
    
    class Config:
        """Pydantic config for LogicalOperator model."""
        
        extra = "allow"  # Allow any additional fields
        allow_population_by_field_name = True


class WhereFilter(BaseModel):
    """Where filter for querying collections."""
    
    class Config:
        """Pydantic config for WhereFilter model."""
        
        extra = "allow"  # Allow any additional fields
        
        schema_extra = {
            "example": {
                "metadata_field": {"$eq": "value"},
                "numeric_field": {"$gt": 10, "$lt": 20},
                "$or": [
                    {"field1": {"$eq": "value1"}},
                    {"field2": {"$eq": "value2"}}
                ]
            }
        }


class DocumentFilter(BaseModel):
    """Document filter for querying collections."""
    
    contains: Optional[str] = Field(None, alias="$contains", description="Document contains this text")
    
    class Config:
        """Pydantic config for DocumentFilter model."""
        
        extra = "allow"  # Allow any additional fields
        allow_population_by_field_name = True
        
        schema_extra = {
            "example": {
                "$contains": "search term"
            }
        }