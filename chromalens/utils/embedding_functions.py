"""
Embedding function utilities for ChromaLens.

This module provides helper functions and classes for generating embeddings.
"""

import logging
import importlib
from typing import Any, Callable, Dict, List, Optional, Union, Tuple, Type
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingFunction:
    """Base class for embedding functions."""
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement __call__")


class DefaultEmbeddingFunction(EmbeddingFunction):
    """
    Default embedding function using all-zeros embeddings.
    
    This is a placeholder for when no embedding function is provided.
    """
    
    def __init__(self, dimension: int = 768):
        """
        Initialize with a specified dimension.
        
        Args:
            dimension: Dimensionality of the embeddings
        """
        self.dimension = dimension
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        Generate all-zeros embeddings.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of all-zeros embedding vectors
        """
        logger.warning("Using default embedding function with all-zeros embeddings")
        return [[0.0] * self.dimension for _ in texts]


class OpenAIEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function using the OpenAI API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "text-embedding-ada-002",
        dimensions: Optional[int] = None,
        batch_size: int = 100,
    ):
        """
        Initialize the OpenAI embedding function.
        
        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model_name: Name of the OpenAI embedding model to use
            dimensions: Output dimensionality (if supported by the model)
            batch_size: Batch size for API calls
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "The OpenAI package is not installed. "
                "Please install it with `pip install openai`."
            )
        
        self.openai_client = None
        if hasattr(openai, "OpenAI"):  # OpenAI v1+
            self.openai_client = openai.OpenAI(api_key=api_key)
            self._call_fn = self._call_v1
        else:  # Legacy OpenAI
            openai.api_key = api_key
            self._call_fn = self._call_legacy
        
        self.model_name = model_name
        self.dimensions = dimensions
        self.batch_size = batch_size
    
    def _call_legacy(self, texts: List[str]) -> List[List[float]]:
        """
        Call the OpenAI API using the legacy client.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        import openai
        
        kwargs = {"engine": self.model_name, "input": texts}
        if self.dimensions is not None:
            kwargs["dimensions"] = self.dimensions
        
        response = openai.Embedding.create(**kwargs)
        return [data["embedding"] for data in response["data"]]
    
    def _call_v1(self, texts: List[str]) -> List[List[float]]:
        """
        Call the OpenAI API using the v1 client.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        kwargs = {"model": self.model_name, "input": texts}
        if self.dimensions is not None:
            kwargs["dimensions"] = self.dimensions
        
        response = self.openai_client.embeddings.create(**kwargs)
        return [data.embedding for data in response.data]
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using the OpenAI API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Process in batches to avoid hitting API limits
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i+self.batch_size]
            batch_embeddings = self._call_fn(batch_texts)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings


class HuggingFaceEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function using Hugging Face models.
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        batch_size: int = 32,
        device: Optional[str] = None,
    ):
        """
        Initialize the Hugging Face embedding function.
        
        Args:
            model_name: Name of the Hugging Face model to use
            batch_size: Batch size for model inference
            device: Device to use for model inference (e.g., "cpu", "cuda")
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "The sentence-transformers package is not installed. "
                "Please install it with `pip install sentence-transformers`."
            )
        
        self.model_name = model_name
        self.batch_size = batch_size
        
        # Load model
        self.model = SentenceTransformer(model_name, device=device)
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using the Hugging Face model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        
        # Convert from numpy to list
        return embeddings.tolist()


class CohereEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function using the Cohere API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "embed-english-v3.0",
        batch_size: int = 96,
        input_type: str = "search_document",
    ):
        """
        Initialize the Cohere embedding function.
        
        Args:
            api_key: Cohere API key (if None, reads from COHERE_API_KEY env var)
            model_name: Name of the Cohere embedding model to use
            batch_size: Batch size for API calls
            input_type: Type of input ("search_document", "search_query", etc.)
        """
        try:
            import cohere
        except ImportError:
            raise ImportError(
                "The cohere package is not installed. "
                "Please install it with `pip install cohere`."
            )
        
        self.client = cohere.Client(api_key)
        self.model_name = model_name
        self.batch_size = batch_size
        self.input_type = input_type
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using the Cohere API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Process in batches to avoid hitting API limits
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i+self.batch_size]
            response = self.client.embed(
                texts=batch_texts,
                model=self.model_name,
                input_type=self.input_type,
            )
            all_embeddings.extend(response.embeddings)
        
        return all_embeddings


def get_embedding_function(
    provider: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> EmbeddingFunction:
    """
    Get an embedding function by provider name.
    
    Args:
        provider: Name of the embedding provider (openai, huggingface, cohere, etc.)
        api_key: API key for the provider (if required)
        model_name: Name of the model to use
        **kwargs: Additional arguments for the embedding function
        
    Returns:
        An embedding function instance
        
    Raises:
        ValueError: If the provider is not supported
    """
    provider = provider.lower()
    
    if provider == "openai":
        model = model_name or "text-embedding-ada-002"
        return OpenAIEmbeddingFunction(api_key=api_key, model_name=model, **kwargs)
    
    elif provider == "huggingface" or provider == "hf":
        model = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        return HuggingFaceEmbeddingFunction(model_name=model, **kwargs)
    
    elif provider == "cohere":
        model = model_name or "embed-english-v3.0"
        return CohereEmbeddingFunction(api_key=api_key, model_name=model, **kwargs)
    
    elif provider == "default":
        dimension = kwargs.get("dimension", 768)
        return DefaultEmbeddingFunction(dimension=dimension)
    
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def text_to_embeddings(
    texts: List[str],
    provider: str = "default",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    dimension: int = 768,
    **kwargs
) -> List[List[float]]:
    """
    Convert texts to embeddings using the specified provider.
    
    Args:
        texts: List of texts to embed
        provider: Name of the embedding provider
        api_key: API key for the provider (if required)
        model_name: Name of the model to use
        dimension: Dimensionality for the default embedding function
        **kwargs: Additional arguments for the embedding function
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    # Get the embedding function
    embedding_fn = get_embedding_function(
        provider=provider,
        api_key=api_key,
        model_name=model_name,
        dimension=dimension,
        **kwargs
    )
    
    # Generate embeddings
    return embedding_fn(texts)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity (between -1 and 1)
    """
    # Convert to numpy arrays
    a = np.array(vec1)
    b = np.array(vec2)
    
    # Calculate cosine similarity
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    # Handle zero vectors
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate Euclidean distance between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Euclidean distance
    """
    # Convert to numpy arrays
    a = np.array(vec1)
    b = np.array(vec2)
    
    # Calculate Euclidean distance
    return np.linalg.norm(a - b)