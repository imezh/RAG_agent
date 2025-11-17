"""PDF document parser."""

import logging
from pathlib import Path
from typing import List

from pypdf import PdfReader

from .base import BaseParser, Document

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """Parser for PDF documents."""

    def parse(self, file_path: Path) -> List[Document]:
        """
        Parse a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of Document objects (one per page)
        """
        try:
            documents = []
            reader = PdfReader(str(file_path))

            for page_num, page in enumerate(reader.pages, start=1):
                # Extract text
                text = page.extract_text()

                if not text.strip():
                    logger.warning(f"Page {page_num} of {file_path.name} is empty")
                    continue

                # Clean text
                text = self._clean_text(text)

                # Extract metadata
                metadata = {
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "page_number": page_num,
                    "total_pages": len(reader.pages),
                }

                # Add PDF metadata if available
                if reader.metadata:
                    metadata.update(
                        {
                            "title": reader.metadata.get("/Title", ""),
                            "author": reader.metadata.get("/Author", ""),
                            "subject": reader.metadata.get("/Subject", ""),
                            "creator": reader.metadata.get("/Creator", ""),
                        }
                    )

                # Extract tables if enabled
                tables = []
                if self.extract_tables:
                    tables = self._extract_tables_from_page(page)

                # Create document
                doc = Document(
                    text=text,
                    metadata=metadata,
                    tables=tables,
                    source=str(file_path),
                    page_number=page_num,
                )
                documents.append(doc)

            logger.info(
                f"Parsed {len(documents)} pages from {file_path.name}"
            )
            return documents

        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise

    def _extract_tables_from_page(self, page) -> List[dict]:
        """
        Extract tables from a PDF page.

        Note: Basic implementation. For better table extraction,
        consider using libraries like camelot-py or tabula-py.

        Args:
            page: PDF page object

        Returns:
            List of table dictionaries
        """
        # This is a placeholder for table extraction
        # You can implement more sophisticated table extraction using:
        # - camelot-py
        # - tabula-py
        # - pdfplumber
        return []
