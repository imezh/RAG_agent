"""Base parser class and document model."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Document:
    """Document model for parsed content."""

    text: str
    metadata: Dict = field(default_factory=dict)
    tables: List[Dict] = field(default_factory=list)
    source: Optional[str] = None
    page_number: Optional[int] = None

    def __post_init__(self):
        """Post initialization to set default source."""
        if self.source and isinstance(self.source, Path):
            self.source = str(self.source)


class BaseParser(ABC):
    """Base class for document parsers."""

    def __init__(self, extract_tables: bool = True):
        """
        Initialize parser.

        Args:
            extract_tables: Whether to extract tables from documents
        """
        self.extract_tables = extract_tables

    @abstractmethod
    def parse(self, file_path: Path) -> List[Document]:
        """
        Parse a document file.

        Args:
            file_path: Path to the document file

        Returns:
            List of parsed Document objects
        """
        pass

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = " ".join(text.split())
        # Remove multiple newlines
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
        return text

    @staticmethod
    def get_parser(file_path: Path, **kwargs) -> "BaseParser":
        """
        Get appropriate parser based on file extension.

        Args:
            file_path: Path to the document file
            **kwargs: Additional arguments for parser initialization

        Returns:
            Appropriate parser instance

        Raises:
            ValueError: If file format is not supported
        """
        from .docx_parser import DOCXParser
        from .pdf_parser import PDFParser
        from .text_parser import TextParser

        extension = file_path.suffix.lower()

        parsers = {
            ".pdf": PDFParser,
            ".docx": DOCXParser,
            ".doc": DOCXParser,
            ".md": TextParser,
            ".txt": TextParser,
        }

        parser_class = parsers.get(extension)
        if parser_class is None:
            raise ValueError(f"Unsupported file format: {extension}")

        return parser_class(**kwargs)
