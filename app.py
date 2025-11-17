"""Streamlit web interface for Document QA Agent."""

import logging
import sys
from pathlib import Path

import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import config
from embeddings import Embedder, TextSplitter, VectorStore
from parsers import BaseParser
from rag import RAGPipeline, YandexGPTClient, GigaChatClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Page configuration
st.set_page_config(
    page_title="Document QA Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.embedder = None
    st.session_state.vector_store = None
    st.session_state.rag_pipeline = None
    st.session_state.chat_history = []


def initialize_system():
    """Initialize the QA system."""
    try:
        with st.spinner("Инициализация системы..."):
            # Initialize embedder
            st.session_state.embedder = Embedder(
                model_name=config.embeddings.model,
                batch_size=config.embeddings.batch_size,
            )

            # Initialize vector store
            st.session_state.vector_store = VectorStore(
                persist_directory=config.vectordb.persist_directory,
                collection_name=config.vectordb.collection_name,
                distance_metric=config.vectordb.distance_metric,
            )

            # Initialize LLM client
            if config.llm.provider == "yandexgpt":
                llm_client = YandexGPTClient(
                    api_key=config.llm.api_key,
                    folder_id=config.llm.folder_id,
                    model=config.llm.model,
                    temperature=config.llm.temperature,
                    max_tokens=config.llm.max_tokens,
                )
            elif config.llm.provider == "gigachat":
                llm_client = GigaChatClient(
                    api_key=config.llm.api_key,
                    model=config.llm.model,
                    temperature=config.llm.temperature,
                    max_tokens=config.llm.max_tokens,
                )
            else:
                st.error(f"Unsupported LLM provider: {config.llm.provider}")
                return False

            # Initialize RAG pipeline
            st.session_state.rag_pipeline = RAGPipeline(
                llm_client=llm_client,
                embedder=st.session_state.embedder,
                vector_store=st.session_state.vector_store,
                top_k=config.retrieval.top_k,
                relevance_threshold=config.retrieval.relevance_threshold,
            )

            st.session_state.initialized = True
            return True

    except Exception as e:
        st.error(f"Ошибка инициализации: {e}")
        logger.error(f"Initialization error: {e}", exc_info=True)
        return False


def process_uploaded_files(uploaded_files):
    """Process and index uploaded documents."""
    if not uploaded_files:
        return

    with st.spinner("Обработка документов..."):
        text_splitter = TextSplitter(
            chunk_size=config.embeddings.chunk_size,
            chunk_overlap=config.embeddings.chunk_overlap,
        )

        all_chunks = []

        for uploaded_file in uploaded_files:
            try:
                # Save uploaded file temporarily
                temp_path = Path(config.app.raw_docs_dir) / uploaded_file.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Parse document
                parser = BaseParser.get_parser(
                    temp_path,
                    extract_tables=config.parsing.extract_tables,
                )
                documents = parser.parse(temp_path)

                # Convert to dict format
                doc_dicts = [
                    {"text": doc.text, "metadata": doc.metadata}
                    for doc in documents
                ]

                # Split into chunks
                chunks = text_splitter.split_documents(doc_dicts)
                all_chunks.extend(chunks)

                st.success(f"Обработан: {uploaded_file.name}")

            except Exception as e:
                st.error(f"Ошибка обработки {uploaded_file.name}: {e}")
                logger.error(f"Error processing {uploaded_file.name}: {e}", exc_info=True)

        if all_chunks:
            # Generate embeddings
            texts = [chunk["text"] for chunk in all_chunks]
            metadatas = [chunk["metadata"] for chunk in all_chunks]

            embeddings = st.session_state.embedder.embed_texts(
                texts,
                show_progress=False,
            )

            # Add to vector store
            st.session_state.vector_store.add_documents(
                texts=texts,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
            )

            st.success(f"Проиндексировано {len(all_chunks)} фрагментов из {len(uploaded_files)} документов")


def main():
    """Main application."""
    st.title("📚 Document QA Agent")
    st.markdown("*Система ответов на вопросы по внутренним нормативным документам*")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Управление")

        # System status
        st.subheader("Статус системы")
        if st.session_state.initialized:
            st.success("✅ Система готова")
            if st.session_state.vector_store:
                doc_count = st.session_state.vector_store.get_collection_count()
                st.info(f"📄 Документов в базе: {doc_count}")
        else:
            st.warning("⏳ Требуется инициализация")
            if st.button("Инициализировать систему"):
                if initialize_system():
                    st.rerun()

        st.divider()

        # Document upload
        st.subheader("📤 Загрузка документов")
        uploaded_files = st.file_uploader(
            "Выберите документы",
            type=["pdf", "docx", "doc", "md", "txt"],
            accept_multiple_files=True,
        )

        if uploaded_files and st.button("Обработать документы"):
            if not st.session_state.initialized:
                st.error("Сначала инициализируйте систему")
            else:
                process_uploaded_files(uploaded_files)

        st.divider()

        # Settings
        st.subheader("🔧 Настройки")
        st.info(f"""
        **LLM:** {config.llm.provider}
        **Модель:** {config.llm.model}
        **Top-K:** {config.retrieval.top_k}
        **Порог релевантности:** {config.retrieval.relevance_threshold}
        """)

        if st.button("Очистить историю"):
            st.session_state.chat_history = []
            st.rerun()

    # Main area
    if not st.session_state.initialized:
        st.info("👈 Пожалуйста, инициализируйте систему через боковую панель")
        return

    # Chat interface
    st.subheader("💬 Задайте вопрос")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander(f"📚 Источники ({message.get('num_sources', 0)})"):
                    for i, source in enumerate(message["sources"], 1):
                        metadata = source.get("metadata", {})
                        st.markdown(f"""
                        **Источник {i}** (релевантность: {source.get('similarity', 0):.2%})
                        *Файл:* {metadata.get('file_name', 'Unknown')}
                        *Страница:* {metadata.get('page_number', 'N/A')}

                        {source.get('text', '')}
                        """)
                        st.divider()

    # Chat input
    if query := st.chat_input("Введите ваш вопрос..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Поиск ответа..."):
                result = st.session_state.rag_pipeline.answer_question(query)

                st.markdown(result["answer"])

                # Show sources
                if result.get("sources"):
                    with st.expander(f"📚 Источники ({result['num_sources']})"):
                        for i, source in enumerate(result["sources"], 1):
                            metadata = source.get("metadata", {})
                            st.markdown(f"""
                            **Источник {i}** (релевантность: {source.get('similarity', 0):.2%})
                            *Файл:* {metadata.get('file_name', 'Unknown')}
                            *Страница:* {metadata.get('page_number', 'N/A')}

                            {source.get('text', '')}
                            """)
                            st.divider()

        # Add assistant message
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get("sources", []),
                "num_sources": result.get("num_sources", 0),
            }
        )


if __name__ == "__main__":
    main()
