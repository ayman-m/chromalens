"""
Configuration module for ChromaLens client.
"""

from chromalens.config.settings import (
    DEFAULT_TIMEOUT,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_DIMENSION,
    MAX_BATCH_SIZE,
    DEFAULT_API_VERSION,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_LOG_LEVEL,
    get_settings,
    load_settings_from_env,
)

from chromalens.config.constants import (
    API_V1,
    API_V2,
    DEFAULT_TENANT,
    DEFAULT_DATABASE,
)

__all__ = [
    # Settings
    'DEFAULT_TIMEOUT',
    'DEFAULT_CHUNK_SIZE',
    'DEFAULT_DIMENSION',
    'MAX_BATCH_SIZE',
    'DEFAULT_API_VERSION',
    'DEFAULT_HOST',
    'DEFAULT_PORT',
    'DEFAULT_LOG_LEVEL',
    'get_settings',
    'load_settings_from_env',
    
    # Constants
    'API_V1',
    'API_V2',
    'DEFAULT_TENANT',
    'DEFAULT_DATABASE',
]