"""
Configuration settings for the ChromaLens client.
"""

import os
from typing import Dict, Any, Optional

# Default request timeout in seconds
DEFAULT_TIMEOUT = 60.0

# Default chunk size for streaming operations (in bytes)
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB

# Default embedding dimension
DEFAULT_DIMENSION = 768

# Maximum number of items in batch operations
MAX_BATCH_SIZE = 1000

# Default API version to use
DEFAULT_API_VERSION = "v2"

# Default host and port
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000

# Default logging level
DEFAULT_LOG_LEVEL = "INFO"

# Environment variable names for configuration
ENV_PREFIX = "CHROMALENS_"
ENV_HOST = f"{ENV_PREFIX}HOST"
ENV_PORT = f"{ENV_PREFIX}PORT"
ENV_TENANT = f"{ENV_PREFIX}TENANT"
ENV_DATABASE = f"{ENV_PREFIX}DATABASE"
ENV_SSL = f"{ENV_PREFIX}SSL"
ENV_TIMEOUT = f"{ENV_PREFIX}TIMEOUT"
ENV_API_KEY = f"{ENV_PREFIX}API_KEY"
ENV_LOG_LEVEL = f"{ENV_PREFIX}LOG_LEVEL"

def load_settings_from_env() -> Dict[str, Any]:
    """
    Load settings from environment variables.
    
    Returns:
        Dictionary of settings loaded from environment variables
    """
    settings = {}
    
    # Host setting
    if ENV_HOST in os.environ:
        settings["host"] = os.environ[ENV_HOST]
    
    # Port setting
    if ENV_PORT in os.environ:
        try:
            settings["port"] = int(os.environ[ENV_PORT])
        except ValueError:
            # Log warning but continue with default
            pass
    
    # Tenant setting
    if ENV_TENANT in os.environ:
        settings["tenant"] = os.environ[ENV_TENANT]
    
    # Database setting
    if ENV_DATABASE in os.environ:
        settings["database"] = os.environ[ENV_DATABASE]
    
    # SSL setting
    if ENV_SSL in os.environ:
        ssl_value = os.environ[ENV_SSL].lower()
        settings["ssl"] = ssl_value in ("true", "1", "yes")
    
    # Timeout setting
    if ENV_TIMEOUT in os.environ:
        try:
            settings["timeout"] = float(os.environ[ENV_TIMEOUT])
        except ValueError:
            # Log warning but continue with default
            pass
    
    # API key setting
    if ENV_API_KEY in os.environ:
        settings["api_key"] = os.environ[ENV_API_KEY]
    
    return settings


def get_settings(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get the effective settings, merging defaults, environment variables, and overrides.
    
    Args:
        overrides: Dictionary of settings that override defaults and environment variables
        
    Returns:
        Dictionary of effective settings
    """
    # Start with defaults
    settings = {
        "host": DEFAULT_HOST,
        "port": DEFAULT_PORT,
        "timeout": DEFAULT_TIMEOUT,
        "api_version": DEFAULT_API_VERSION,
        "ssl": False,
        "verify_ssl": True,
    }
    
    # Apply environment variables
    settings.update(load_settings_from_env())
    
    # Apply overrides
    if overrides:
        settings.update(overrides)
    
    return settings