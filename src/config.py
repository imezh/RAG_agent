"""Configuration management for Document QA Agent."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


# Load environment variables
load_dotenv()


class LLMConfig(BaseSettings):
    """LLM configuration."""

    provider: str = "yandexgpt"
    model: str = "yandexgpt-lite"
    temperature: float = 0.3
    max_tokens: int = 2000
    api_key: str = Field(default="", alias="YANDEX_API_KEY")
    folder_id: str = Field(default="", alias="YANDEX_FOLDER_ID")

    class Config:
        env_file = ".env"
        extra = "allow"


class EmbeddingsConfig(BaseSettings):
    """Embeddings configuration."""

    model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    chunk_size: int = 500
    chunk_overlap: int = 100
    batch_size: int = 32


class VectorDBConfig(BaseSettings):
    """Vector database configuration."""

    type: str = "chromadb"
    persist_directory: str = "./data/vectordb"
    collection_name: str = "documents"
    distance_metric: str = "cosine"


class RetrievalConfig(BaseSettings):
    """Retrieval configuration."""

    top_k: int = 5
    relevance_threshold: float = 0.7
    rerank: bool = True


class ParsingConfig(BaseSettings):
    """Document parsing configuration."""

    supported_formats: list = ["pdf", "docx", "md", "txt"]
    extract_tables: bool = True
    extract_images: bool = False
    ocr_enabled: bool = False


class AppConfig(BaseSettings):
    """Application configuration."""

    name: str = "Document QA Agent"
    version: str = "1.0.0"
    data_dir: str = "./data"
    raw_docs_dir: str = "./data/raw"
    processed_docs_dir: str = "./data/processed"


class Config:
    """Main configuration class."""

    def __init__(self, config_path: str = "configs/config.yaml"):
        """Initialize configuration from YAML file."""
        self.config_path = Path(config_path)
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Initialize sub-configurations
        self.llm = LLMConfig(**config_data.get("llm", {}))
        self.embeddings = EmbeddingsConfig(**config_data.get("embeddings", {}))
        self.vectordb = VectorDBConfig(**config_data.get("vectordb", {}))
        self.retrieval = RetrievalConfig(**config_data.get("retrieval", {}))
        self.parsing = ParsingConfig(**config_data.get("parsing", {}))
        self.app = AppConfig(**config_data.get("app", {}))

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(self, key, default)


# Global configuration instance
config = Config()
