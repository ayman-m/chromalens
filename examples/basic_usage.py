"""
Basic usage example for ChromaLens
"""
from chromalens.client import ChromaLensClient

# Initialize client
client = ChromaLensClient(host="localhost", port=8000)

# Check connection
try:
    heartbeat = client.heartbeat()
    print(f"Connected to ChromaDB! Heartbeat: {heartbeat}")
except Exception as e:
    print(f"Failed to connect: {e}")
