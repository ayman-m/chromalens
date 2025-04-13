"""
Database models for ChromaLens.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class DatabaseCreate(BaseModel):
    """Model for creating a database."""
    
    name: str = Field(..., description="Name of the database")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        """Validate database name format."""
        if not v or not v.strip():
            raise ValueError("Database name cannot be empty")
        if len(v) > 64:
            raise ValueError("Database name cannot exceed 64 characters")
        # Add additional validation rules if needed
        return v


class Database(BaseModel):
    """Model for a database."""
    
    id: str = Field(..., description="Unique ID of the database")
    name: str = Field(..., description="Name of the database")
    tenant: str = Field(..., description="Tenant the database belongs to")
    
    class Config:
        """Pydantic config for Database model."""
        
        schema_extra = {
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "name": "default_database",
                "tenant": "default_tenant"
            }
        }


class DatabasesResponse(BaseModel):
    """Model for a list of databases response."""
    
    databases: list[Database] = Field(..., description="List of databases")
    
    class Config:
        """Pydantic config for DatabasesResponse model."""
        
        schema_extra = {
            "example": {
                "databases": [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "name": "default_database",
                        "tenant": "default_tenant"
                    },
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "name": "custom_database",
                        "tenant": "default_tenant"
                    }
                ]
            }
        }


class DatabaseUpdateRequest(BaseModel):
    """Model for updating a database (if supported)."""
    
    new_name: Optional[str] = Field(None, description="New name for the database")
    
    @validator('new_name')
    def name_must_be_valid(cls, v):
        """Validate database name format."""
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Database name cannot be empty")
        if len(v) > 64:
            raise ValueError("Database name cannot exceed 64 characters")
        # Add additional validation rules if needed
        return v


class DatabaseCountResponse(BaseModel):
    """Model for a database collection count response."""
    
    count: int = Field(..., description="Number of collections in the database")
    
    class Config:
        """Pydantic config for DatabaseCountResponse model."""
        
        schema_extra = {
            "example": {
                "count": 5
            }
        }