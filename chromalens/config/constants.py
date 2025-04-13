"""
Constants used throughout the ChromaLens client.
"""

# API versions
API_V1 = "v1"
API_V2 = "v2"

# Default values
DEFAULT_TENANT = "default_tenant"
DEFAULT_DATABASE = "default_database"

# HTTP methods
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"

# Content types
CONTENT_TYPE_JSON = "application/json"

# Status codes for specific error handling
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_NO_CONTENT = 204
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_CONFLICT = 409
STATUS_UNPROCESSABLE_ENTITY = 422
STATUS_SERVER_ERROR = 500

# Endpoint paths
ENDPOINT_HEARTBEAT = "heartbeat"
ENDPOINT_VERSION = "version"
ENDPOINT_RESET = "reset"
ENDPOINT_PRE_FLIGHT_CHECKS = "pre-flight-checks"

# Tenant endpoints
ENDPOINT_TENANTS = "tenants"

# Database endpoints
ENDPOINT_DATABASES = "databases"

# Collection endpoints
ENDPOINT_COLLECTIONS = "collections"
ENDPOINT_ADD = "add"
ENDPOINT_UPDATE = "update"
ENDPOINT_UPSERT = "upsert"
ENDPOINT_GET = "get"
ENDPOINT_DELETE = "delete"
ENDPOINT_COUNT = "count"
ENDPOINT_QUERY = "query"

# Authentication endpoints
ENDPOINT_AUTH_IDENTITY = "auth/identity"

# Query parameters
PARAM_TENANT = "tenant"
PARAM_DATABASE = "database"
PARAM_LIMIT = "limit"
PARAM_OFFSET = "offset"

# Request/response fields
FIELD_NAME = "name"
FIELD_ID = "id"
FIELD_METADATA = "metadata"
FIELD_TENANT = "tenant"
FIELD_DATABASE = "database"
FIELD_DIMENSION = "dimension"
FIELD_IDS = "ids"
FIELD_EMBEDDINGS = "embeddings"
FIELD_METADATAS = "metadatas"
FIELD_DOCUMENTS = "documents"
FIELD_URIS = "uris"
FIELD_WHERE = "where"
FIELD_WHERE_DOCUMENT = "where_document"
FIELD_N_RESULTS = "n_results"
FIELD_INCLUDE = "include"