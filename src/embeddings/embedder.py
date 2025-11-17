"""Embedding generation using sentence transformers."""

import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class Embedder:
    """Generate embeddings for text using sentence transformers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        batch_size: int = 32,
    ):
        """
        Initialize embedder.

        Args:
            model_name: Name or path of the sentence transformer model
            batch_size: Batch size for encoding
        """
        self.model_name = model_name
        self.batch_size = batch_size

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress bar

        Returns:
            Array of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()
