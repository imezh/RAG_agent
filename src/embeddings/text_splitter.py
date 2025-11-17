"""Text splitting utilities for chunking documents."""

import logging
from typing import List

logger = logging.getLogger(__name__)


class TextSplitter:
    """Split text into chunks with overlap."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize text splitter.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence or paragraph boundary
            if end < len(text):
                # Look for paragraph break first
                paragraph_break = text.rfind("\n\n", start, end)
                if paragraph_break > start:
                    end = paragraph_break + 2
                else:
                    # Look for sentence break
                    sentence_breaks = [". ", "! ", "? ", ".\n", "!\n", "?\n"]
                    for break_char in sentence_breaks:
                        break_pos = text.rfind(break_char, start, end)
                        if break_pos > start:
                            end = break_pos + len(break_char)
                            break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = end

        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

    def split_documents(self, documents: List[dict]) -> List[dict]:
        """
        Split multiple documents into chunks.

        Args:
            documents: List of document dictionaries with 'text' and 'metadata' keys

        Returns:
            List of chunk dictionaries with text, metadata, and chunk_id
        """
        all_chunks = []

        for doc_idx, doc in enumerate(documents):
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            chunks = self.split_text(text)

            for chunk_idx, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata.update(
                    {
                        "doc_id": doc_idx,
                        "chunk_id": f"{doc_idx}_{chunk_idx}",
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                    }
                )

                all_chunks.append({"text": chunk, "metadata": chunk_metadata})

        logger.info(f"Split {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
