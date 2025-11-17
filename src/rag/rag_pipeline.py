"""RAG pipeline for question answering."""

import logging
from typing import Dict, List, Optional

from ..embeddings import Embedder, VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for document question answering."""

    def __init__(
        self,
        llm_client,
        embedder: Embedder,
        vector_store: VectorStore,
        top_k: int = 5,
        relevance_threshold: float = 0.7,
    ):
        """
        Initialize RAG pipeline.

        Args:
            llm_client: LLM client for generation
            embedder: Embedder for query encoding
            vector_store: Vector store for document retrieval
            top_k: Number of documents to retrieve
            relevance_threshold: Minimum relevance score
        """
        self.llm_client = llm_client
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k
        self.relevance_threshold = relevance_threshold

        logger.info("Initialized RAG pipeline")

    def retrieve_context(self, query: str) -> List[Dict]:
        """
        Retrieve relevant context documents for a query.

        Args:
            query: User query

        Returns:
            List of relevant document dictionaries
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query)

        # Search for similar documents
        results = self.vector_store.search(
            query_embedding=query_embedding.tolist(),
            top_k=self.top_k,
        )

        # Filter by relevance threshold
        relevant_docs = []
        for doc, distance, metadata in zip(
            results["documents"],
            results["distances"],
            results["metadatas"],
        ):
            # Convert distance to similarity score (for cosine distance)
            similarity = 1 - distance

            if similarity >= self.relevance_threshold:
                relevant_docs.append(
                    {
                        "text": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                    }
                )

        logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
        return relevant_docs

    def generate_prompt(self, query: str, context_docs: List[Dict]) -> str:
        """
        Generate prompt with context for the LLM.

        Args:
            query: User query
            context_docs: List of context documents

        Returns:
            Formatted prompt
        """
        if not context_docs:
            return f"""Вопрос: {query}

Ответ: К сожалению, я не нашел релевантных документов для ответа на ваш вопрос."""

        # Format context
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            metadata = doc.get("metadata", {})
            source = metadata.get("file_name", "Unknown")
            page = metadata.get("page_number")

            context_part = f"[Документ {i}]"
            if source:
                context_part += f" (Источник: {source}"
                if page:
                    context_part += f", Страница: {page}"
                context_part += ")"
            context_part += f"\n{doc['text']}\n"
            context_parts.append(context_part)

        context = "\n".join(context_parts)

        # Create prompt
        prompt = f"""На основе предоставленных документов ответьте на вопрос пользователя.

КОНТЕКСТ:
{context}

ВОПРОС: {query}

ИНСТРУКЦИИ:
1. Используйте только информацию из предоставленных документов
2. Если информации недостаточно для полного ответа, укажите это
3. Цитируйте источники, упоминая номера документов
4. Отвечайте четко и структурированно
5. Если в документах есть таблицы или формулы, используйте их в ответе

ОТВЕТ:"""

        return prompt

    def generate_system_prompt(self) -> str:
        """
        Generate system prompt for the LLM.

        Returns:
            System prompt
        """
        return """Вы - помощник по работе с внутренними нормативными документами организации.
Ваша задача - отвечать на вопросы пользователей, используя только информацию из предоставленных документов.

Правила работы:
- Будьте точны и используйте только факты из документов
- Структурируйте ответы для лучшей читаемости
- Если в документах есть противоречия, укажите на них
- Если информации недостаточно, честно сообщите об этом
- При упоминании данных из таблиц или формул, представляйте их четко
- Всегда указывайте источники информации"""

    def answer_question(self, query: str) -> Dict:
        """
        Answer a question using RAG.

        Args:
            query: User question

        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing query: {query}")

        # Retrieve relevant context
        context_docs = self.retrieve_context(query)

        # Generate prompt
        prompt = self.generate_prompt(query, context_docs)
        system_prompt = self.generate_system_prompt()

        # Generate answer
        try:
            answer = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
            )

            logger.info("Generated answer successfully")

            return {
                "answer": answer,
                "sources": [
                    {
                        "text": doc["text"][:200] + "...",  # Preview
                        "metadata": doc["metadata"],
                        "similarity": doc["similarity"],
                    }
                    for doc in context_docs
                ],
                "num_sources": len(context_docs),
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "Произошла ошибка при генерации ответа. Пожалуйста, попробуйте позже.",
                "sources": [],
                "num_sources": 0,
                "error": str(e),
            }
