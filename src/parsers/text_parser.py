"""Text and Markdown document parser."""

import logging
from pathlib import Path
from typing import List

import markdown

from .base import BaseParser, Document

logger = logging.getLogger(__name__)


class TextParser(BaseParser):
    """Parser for text and Markdown documents."""

    def parse(self, file_path: Path) -> List[Document]:
        """
        Parse a text or Markdown document.

        Args:
            file_path: Path to the text file

        Returns:
            List containing a single Document object
        """
        try:
            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Convert Markdown to plain text if needed
            if file_path.suffix.lower() == ".md":
                text = self._markdown_to_text(text)

            text = self._clean_text(text)

            # Extract metadata
            metadata = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix.lower(),
                "size_bytes": file_path.stat().st_size,
            }

            # Create document
            document = Document(
                text=text,
                metadata=metadata,
                source=str(file_path),
            )

            logger.info(f"Parsed text document: {file_path.name}")
            return [document]

        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {e}")
            raise

    def _markdown_to_text(self, md_text: str) -> str:
        """
        Convert Markdown to plain text.

        Args:
            md_text: Markdown text

        Returns:
            Plain text
        """
        # Convert to HTML first
        html = markdown.markdown(md_text)

        # Simple HTML tag removal (for better results, use BeautifulSoup)
        import re

        text = re.sub("<[^<]+?>", "", html)
        return text
