"""Tests for document parsers."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parsers import BaseParser, Document, PDFParser, DOCXParser, TextParser


class TestBaseParser:
    """Tests for BaseParser."""

    def test_clean_text(self):
        """Test text cleaning."""
        parser = TextParser()
        text = "  Multiple   spaces   \n\n\n  Multiple newlines  "
        cleaned = parser._clean_text(text)

        assert "  " not in cleaned
        assert "\n\n\n" not in cleaned

    def test_get_parser_pdf(self):
        """Test getting PDF parser."""
        parser = BaseParser.get_parser(Path("test.pdf"))
        assert isinstance(parser, PDFParser)

    def test_get_parser_docx(self):
        """Test getting DOCX parser."""
        parser = BaseParser.get_parser(Path("test.docx"))
        assert isinstance(parser, DOCXParser)

    def test_get_parser_text(self):
        """Test getting text parser."""
        parser = BaseParser.get_parser(Path("test.txt"))
        assert isinstance(parser, TextParser)

    def test_get_parser_markdown(self):
        """Test getting markdown parser."""
        parser = BaseParser.get_parser(Path("test.md"))
        assert isinstance(parser, TextParser)

    def test_get_parser_unsupported(self):
        """Test unsupported format."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            BaseParser.get_parser(Path("test.xyz"))


class TestDocument:
    """Tests for Document model."""

    def test_document_creation(self):
        """Test document creation."""
        doc = Document(
            text="Test text",
            metadata={"key": "value"},
            source="test.pdf",
            page_number=1,
        )

        assert doc.text == "Test text"
        assert doc.metadata["key"] == "value"
        assert doc.source == "test.pdf"
        assert doc.page_number == 1

    def test_document_defaults(self):
        """Test document default values."""
        doc = Document(text="Test text")

        assert doc.text == "Test text"
        assert doc.metadata == {}
        assert doc.tables == []
        assert doc.source is None
        assert doc.page_number is None


class TestTextParser:
    """Tests for TextParser."""

    def test_parse_text_file(self, tmp_path):
        """Test parsing text file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content\nLine 2", encoding="utf-8")

        # Parse
        parser = TextParser()
        documents = parser.parse(test_file)

        assert len(documents) == 1
        assert "Test content" in documents[0].text
        assert "Line 2" in documents[0].text
        assert documents[0].metadata["file_name"] == "test.txt"

    def test_parse_markdown_file(self, tmp_path):
        """Test parsing markdown file."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Header\n\nParagraph", encoding="utf-8")

        # Parse
        parser = TextParser()
        documents = parser.parse(test_file)

        assert len(documents) == 1
        assert "Header" in documents[0].text
        assert "Paragraph" in documents[0].text

    def test_markdown_to_text(self):
        """Test markdown to text conversion."""
        parser = TextParser()
        md_text = "# Header\n\n**Bold** and *italic*"
        plain_text = parser._markdown_to_text(md_text)

        assert "Header" in plain_text
        assert "Bold" in plain_text
        assert "italic" in plain_text
        assert "#" not in plain_text
        assert "**" not in plain_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
