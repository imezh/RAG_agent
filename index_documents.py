"""Command-line script to index documents."""

import argparse
import logging
import sys
from pathlib import Path

from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import config
from embeddings import Embedder, TextSplitter, VectorStore
from parsers import BaseParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def index_documents(documents_dir: str, clear_existing: bool = False):
    """
    Index documents from a directory.

    Args:
        documents_dir: Directory containing documents
        clear_existing: Whether to clear existing index
    """
    documents_path = Path(documents_dir)

    if not documents_path.exists():
        logger.error(f"Directory does not exist: {documents_dir}")
        return

    # Initialize components
    logger.info("Initializing components...")
    embedder = Embedder(
        model_name=config.embeddings.model,
        batch_size=config.embeddings.batch_size,
    )

    vector_store = VectorStore(
        persist_directory=config.vectordb.persist_directory,
        collection_name=config.vectordb.collection_name,
        distance_metric=config.vectordb.distance_metric,
    )

    if clear_existing:
        logger.info("Clearing existing index...")
        vector_store.delete_collection()
        vector_store = VectorStore(
            persist_directory=config.vectordb.persist_directory,
            collection_name=config.vectordb.collection_name,
            distance_metric=config.vectordb.distance_metric,
        )

    text_splitter = TextSplitter(
        chunk_size=config.embeddings.chunk_size,
        chunk_overlap=config.embeddings.chunk_overlap,
    )

    # Find all documents
    supported_extensions = config.parsing.supported_formats
    document_files = []

    for ext in supported_extensions:
        document_files.extend(documents_path.glob(f"**/*.{ext}"))

    if not document_files:
        logger.warning(f"No documents found in {documents_dir}")
        return

    logger.info(f"Found {len(document_files)} documents")

    # Process documents
    all_chunks = []

    for doc_path in tqdm(document_files, desc="Parsing documents"):
        try:
            # Parse document
            parser = BaseParser.get_parser(
                doc_path,
                extract_tables=config.parsing.extract_tables,
            )
            documents = parser.parse(doc_path)

            # Convert to dict format
            doc_dicts = [
                {"text": doc.text, "metadata": doc.metadata}
                for doc in documents
            ]

            # Split into chunks
            chunks = text_splitter.split_documents(doc_dicts)
            all_chunks.extend(chunks)

        except Exception as e:
            logger.error(f"Error processing {doc_path}: {e}")

    if not all_chunks:
        logger.warning("No chunks generated from documents")
        return

    logger.info(f"Generated {len(all_chunks)} chunks")

    # Generate embeddings
    logger.info("Generating embeddings...")
    texts = [chunk["text"] for chunk in all_chunks]
    metadatas = [chunk["metadata"] for chunk in all_chunks]

    embeddings = embedder.embed_texts(texts, show_progress=True)

    # Add to vector store
    logger.info("Adding to vector store...")
    vector_store.add_documents(
        texts=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    logger.info(f"Successfully indexed {len(all_chunks)} chunks from {len(document_files)} documents")
    logger.info(f"Total documents in vector store: {vector_store.get_collection_count()}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Index documents for the Document QA Agent"
    )
    parser.add_argument(
        "documents_dir",
        type=str,
        help="Directory containing documents to index",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing index before indexing",
    )

    args = parser.parse_args()

    try:
        index_documents(args.documents_dir, args.clear)
    except Exception as e:
        logger.error(f"Error during indexing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
