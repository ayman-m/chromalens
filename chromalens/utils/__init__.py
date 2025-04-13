"""
Utility modules for ChromaLens.
"""

from chromalens.utils.validators import (
    validate_not_empty,
    validate_uuid,
    validate_name,
    validate_embeddings,
    validate_ids,
    validate_lists_same_length,
    validate_metadata,
    validate_documents,
    validate_where_clause,
)

from chromalens.utils.formatters import (
    format_json,
    format_timestamp,
    format_size,
    format_duration,
    format_list,
    format_metadata,
    format_document,
    format_collection_info,
    format_table,
    format_query_results,
)

from chromalens.utils.embedding_functions import (
    EmbeddingFunction,
    DefaultEmbeddingFunction,
    OpenAIEmbeddingFunction,
    HuggingFaceEmbeddingFunction,
    CohereEmbeddingFunction,
    get_embedding_function,
    text_to_embeddings,
    cosine_similarity,
    euclidean_distance,
)

from chromalens.utils.auth import (
    get_api_key,
    get_auth_headers,
    decode_jwt_token,
    is_token_expired,
    get_token_expiration_time,
    get_token_user_info,
)

__all__ = [
    # Validators
    'validate_not_empty',
    'validate_uuid',
    'validate_name',
    'validate_embeddings',
    'validate_ids',
    'validate_lists_same_length',
    'validate_metadata',
    'validate_documents',
    'validate_where_clause',
    
    # Formatters
    'format_json',
    'format_timestamp',
    'format_size',
    'format_duration',
    'format_list',
    'format_metadata',
    'format_document',
    'format_collection_info',
    'format_table',
    'format_query_results',
    
    # Embedding Functions
    'EmbeddingFunction',
    'DefaultEmbeddingFunction',
    'OpenAIEmbeddingFunction',
    'HuggingFaceEmbeddingFunction',
    'CohereEmbeddingFunction',
    'get_embedding_function',
    'text_to_embeddings',
    'cosine_similarity',
    'euclidean_distance',
    
    # Auth
    'get_api_key',
    'get_auth_headers',
    'decode_jwt_token',
    'is_token_expired',
    'get_token_expiration_time',
    'get_token_user_info',
]