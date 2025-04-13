"""
Response models for ChromaLens.
"""

from typing import Optional, Dict, List, Any, Generic, TypeVar, Union
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')


class ErrorDetail(BaseModel):
    """Model for error details."""
    
    loc: List[str] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Model for API error responses."""
    
    detail: Union[str, List[ErrorDetail]] = Field(..., description="Error details")
    
    class Config:
        """Pydantic config for ErrorResponse model."""
        
        schema_extra = {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        }


class SuccessResponse(GenericModel, Generic[T]):
    """Generic model for successful API responses."""
    
    data: T = Field(..., description="Response data")
    status: str = Field("success", description="Response status")
    
    class Config:
        """Pydantic config for SuccessResponse model."""
        
        schema_extra = {
            "example": {
                "data": {},
                "status": "success"
            }
        }


class HeartbeatResponse(BaseModel):
    """Model for the heartbeat response."""
    
    nanosecond_time: int = Field(..., description="Server time in nanoseconds")
    
    class Config:
        """Pydantic config for HeartbeatResponse model."""
        
        schema_extra = {
            "example": {
                "nanosecond_time": 1631234567890123456
            }
        }


class VersionResponse(BaseModel):
    """Model for the version response."""
    
    version: str = Field(..., description="Server version")
    
    class Config:
        """Pydantic config for VersionResponse model."""
        
        schema_extra = {
            "example": {
                "version": "0.4.0"
            }
        }


class ResetResponse(BaseModel):
    """Model for the reset response."""
    
    success: bool = Field(..., description="Whether the reset was successful")
    
    class Config:
        """Pydantic config for ResetResponse model."""
        
        schema_extra = {
            "example": {
                "success": True
            }
        }


class PreFlightCheckResponse(BaseModel):
    """Model for the pre-flight checks response."""
    
    results: Dict[str, Any] = Field(..., description="Pre-flight check results")
    
    class Config:
        """Pydantic config for PreFlightCheckResponse model."""
        
        schema_extra = {
            "example": {
                "results": {
                    "check1": True,
                    "check2": "OK"
                }
            }
        }


class AddResponse(BaseModel):
    """Model for the add response."""
    
    success: bool = Field(True, description="Whether the operation was successful")
    
    class Config:
        """Pydantic config for AddResponse model."""
        
        schema_extra = {
            "example": {
                "success": True
            }
        }


class UpdateResponse(BaseModel):
    """Model for the update response."""
    
    success: bool = Field(True, description="Whether the operation was successful")
    
    class Config:
        """Pydantic config for UpdateResponse model."""
        
        schema_extra = {
            "example": {
                "success": True
            }
        }


class UpsertResponse(BaseModel):
    """Model for the upsert response."""
    
    success: bool = Field(True, description="Whether the operation was successful")
    
    class Config:
        """Pydantic config for UpsertResponse model."""
        
        schema_extra = {
            "example": {
                "success": True
            }
        }


class DeleteResponse(BaseModel):
    """Model for the delete response."""
    
    success: bool = Field(True, description="Whether the operation was successful")
    
    class Config:
        """Pydantic config for DeleteResponse model."""
        
        schema_extra = {
            "example": {
                "success": True
            }
        }