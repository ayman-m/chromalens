"""
Authentication utilities for ChromaLens.

This module provides functions for handling authentication with ChromaDB.
"""

import os
import logging
from typing import Dict, Optional
import base64
import json
import time

logger = logging.getLogger(__name__)


def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """
    Get API key from parameter or environment variable.
    
    Args:
        api_key: API key passed directly, or None to use environment variable
        
    Returns:
        API key if available
    """
    if api_key:
        return api_key
    
    # Try to get from environment variables
    return os.environ.get("CHROMADB_API_KEY") or os.environ.get("CHROMA_API_KEY")


def get_auth_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Get authentication headers for API requests.
    
    Args:
        api_key: API key to use
        
    Returns:
        Dictionary of headers
    """
    headers = {}
    
    api_key = get_api_key(api_key)
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    return headers


def decode_jwt_token(token: str, verify: bool = False) -> Dict:
    """
    Decode a JWT token without validation.
    
    This is for informational purposes only, not for security validation.
    
    Args:
        token: JWT token string
        verify: Whether to verify the token signature (requires PyJWT package)
        
    Returns:
        Decoded token payload
    """
    if verify:
        try:
            import jwt
            return jwt.decode(token, options={"verify_signature": False})
        except ImportError:
            logger.warning("PyJWT package not installed. Install with 'pip install PyJWT' for token verification.")
            verify = False
    
    # Manual decode without verification
    if not verify:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT token format")
        
        # Decode the payload (middle part)
        payload_b64 = parts[1]
        # Add padding if needed
        payload_b64 = payload_b64 + '=' * (4 - len(payload_b64) % 4) if len(payload_b64) % 4 else payload_b64
        
        try:
            payload_bytes = base64.b64decode(payload_b64)
            return json.loads(payload_bytes.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Failed to decode JWT token: {e}")


def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired.
    
    Args:
        token: JWT token string
        
    Returns:
        True if the token is expired, False otherwise
    """
    try:
        payload = decode_jwt_token(token)
        exp = payload.get('exp')
        
        if not exp:
            # No expiration time in the token
            return False
        
        # Check if expired
        return time.time() > exp
    
    except Exception as e:
        # If we can't decode the token, consider it expired
        logger.warning(f"Failed to check token expiration: {e}")
        return True


def get_token_expiration_time(token: str) -> Optional[float]:
    """
    Get the expiration time of a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Expiration time in seconds since epoch, or None if not available
    """
    try:
        payload = decode_jwt_token(token)
        return payload.get('exp')
    
    except Exception as e:
        logger.warning(f"Failed to get token expiration time: {e}")
        return None


def get_token_user_info(token: str) -> Dict:
    """
    Get user information from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary of user information
    """
    try:
        payload = decode_jwt_token(token)
        # Common fields in JWT tokens for user info
        user_info = {
            'user_id': payload.get('sub'),
            'name': payload.get('name'),
            'email': payload.get('email'),
            'roles': payload.get('roles', []),
            'permissions': payload.get('permissions', []),
        }
        return {k: v for k, v in user_info.items() if v is not None}
    
    except Exception as e:
        logger.warning(f"Failed to get user info from token: {e}")
        return {}