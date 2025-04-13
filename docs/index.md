# ChromaLens Documentation

A powerful Python client and intuitive UI for ChromaDB vector database management.

## Installation

```bash
pip install chromalens
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
# Install with UI dependencies
pip install "chromalens[ui]"

# Run the Streamlit app
chromalens-ui
```
