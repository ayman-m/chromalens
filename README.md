# ChromaLens

A powerful Python client and intuitive UI for ChromaDB vector database management.

## Features

- Python client library for ChromaDB
- Streamlit web interface for database management
- Docker support for containerized deployment

## Installation

```bash
# Install the core library
pip install chromalens

# Install with UI dependencies
pip install "chromalens[ui]"
```

## Quick Start

```python
from chromalens.client import ChromaLensClient

# Connect to ChromaDB
client = ChromaLensClient(host="localhost", port=8000)

# Check connection
heartbeat = client.heartbeat()
print(f"Connected to ChromaDB: {heartbeat}")
```

## Running the UI

```bash
# After installing with UI dependencies
chromalens-ui
```

Or run directly with Streamlit:

```bash
streamlit run ui/app.py
```

## Docker

```bash
# Start ChromaDB and ChromaLens UI
docker-compose -f docker/docker-compose.yml up
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
