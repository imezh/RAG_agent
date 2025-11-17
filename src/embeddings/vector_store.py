"""Vector store for document embeddings using ChromaDB."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for storing and retrieving document embeddings."""

    def __init__(
        self,
        persist_directory: str = "./data/vectordb",
        collection_name: str = "documents",
        distance_metric: str = "cosine",
    ):
        """
        Initialize vector store.

        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection
            distance_metric: Distance metric (cosine, l2, ip)
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.distance_metric = distance_metric

        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": distance_metric},
        )

        logger.info(f"Vector store initialized. Collection: {collection_name}")

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for documents
        """
        if not texts:
            logger.warning("No texts to add")
            return

        # Generate IDs if not provided
        if ids is None:
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(texts))]

        # Add to collection
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(f"Added {len(texts)} documents to vector store")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None,
    ) -> Dict:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            Dictionary with documents, distances, and metadatas
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict,
        )

        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "ids": results["ids"][0] if results["ids"] else [],
        }

    def delete_collection(self) -> None:
        """Delete the current collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")

    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.

        Returns:
            Number of documents
        """
        return self.collection.count()

    def update_document(
        self,
        document_id: str,
        text: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Update an existing document.

        Args:
            document_id: ID of the document to update
            text: New text (optional)
            embedding: New embedding (optional)
            metadata: New metadata (optional)
        """
        update_kwargs = {"ids": [document_id]}

        if text is not None:
            update_kwargs["documents"] = [text]
        if embedding is not None:
            update_kwargs["embeddings"] = [embedding]
        if metadata is not None:
            update_kwargs["metadatas"] = [metadata]

        self.collection.update(**update_kwargs)
        logger.info(f"Updated document: {document_id}")

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document by ID.

        Args:
            document_id: ID of the document to delete
        """
        self.collection.delete(ids=[document_id])
        logger.info(f"Deleted document: {document_id}")
