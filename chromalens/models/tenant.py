"""
Tenant models for ChromaLens.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class TenantCreate(BaseModel):
    """Model for creating a tenant."""
    
    name: str = Field(..., description="Name of the tenant")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        """Validate tenant name format."""
        if not v or not v.strip():
            raise ValueError("Tenant name cannot be empty")
        if len(v) > 64:
            raise ValueError("Tenant name cannot exceed 64 characters")
        # Add additional validation rules if needed
        return v


class Tenant(BaseModel):
    """Model for a tenant."""
    
    id: str = Field(..., description="Unique ID of the tenant")
    name: str = Field(..., description="Name of the tenant")
    
    class Config:
        """Pydantic config for Tenant model."""
        
        schema_extra = {
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "name": "default_tenant"
            }
        }


class TenantsResponse(BaseModel):
    """Model for a list of tenants response."""
    
    tenants: list[Tenant] = Field(..., description="List of tenants")
    
    class Config:
        """Pydantic config for TenantsResponse model."""
        
        schema_extra = {
            "example": {
                "tenants": [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "name": "default_tenant"
                    },
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "name": "custom_tenant"
                    }
                ]
            }
        }


class TenantUpdateRequest(BaseModel):
    """Model for updating a tenant (if supported)."""
    
    new_name: Optional[str] = Field(None, description="New name for the tenant")
    
    @validator('new_name')
    def name_must_be_valid(cls, v):
        """Validate tenant name format."""
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Tenant name cannot be empty")
        if len(v) > 64:
            raise ValueError("Tenant name cannot exceed 64 characters")
        # Add additional validation rules if needed
        return v