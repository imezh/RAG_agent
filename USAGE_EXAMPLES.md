# Примеры использования Document QA Agent

## Быстрый старт

### 1. Базовая настройка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env и добавьте свои API ключи
```

### 2. Индексация документов

```bash
# Поместите документы в data/raw/
cp /path/to/your/documents/* data/raw/

# Индексируйте документы
python index_documents.py data/raw
```

### 3. Запуск приложения

```bash
streamlit run app.py
```

## Примеры вопросов

### Пример 1: Простой вопрос

**Вопрос:** "Какие документы необходимы для оформления отпуска?"

**Ответ системы:**
```
На основе внутреннего регламента (Документ 1), для оформления отпуска необходимы следующие документы:

1. Заявление на отпуск (форма ОТП-1)
2. Согласование с непосредственным руководителем
3. Приказ о предоставлении отпуска

Заявление подается не позднее чем за 14 дней до планируемого начала отпуска.

Источник: Регламент по управлению персоналом, раздел 3.2
```

### Пример 2: Вопрос с таблицами

**Вопрос:** "Какие надбавки предусмотрены для сотрудников с опытом работы более 5 лет?"

**Ответ системы:**
```
Согласно положению об оплате труда (Документ 2), для сотрудников с опытом работы более 5 лет предусмотрены следующие надбавки:

- 5-7 лет: 10% к окладу
- 7-10 лет: 15% к окладу
- Более 10 лет: 20% к окладу

Дополнительно предусмотрена ежегодная премия за выслугу лет в размере 50% от месячного оклада.

Источник: Положение об оплате труда, таблица 2, стр. 8
```

### Пример 3: Сложный вопрос

**Вопрос:** "Какова процедура согласования командировки за границу?"

**Ответ системы:**
```
Процедура согласования загранкомандировки включает следующие этапы:

1. Подача заявки (форма КМ-2) минимум за 30 дней
2. Согласование с руководителем подразделения
3. Согласование с финансовым отделом
4. Утверждение генеральным директором
5. Оформление виз и страховки через отдел кадров

Необходимые документы:
- Служебная записка с обоснованием
- Приглашение от принимающей стороны
- Заграничный паспорт (срок действия не менее 6 месяцев)
- Копия предыдущих виз (если имеются)

Источники:
- Положение о командировках, раздел 4 (Документ 1)
- Инструкция по международным поездкам (Документ 3)
```

## Использование через Python API

### Базовое использование

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import config
from embeddings import Embedder, VectorStore
from rag import RAGPipeline, YandexGPTClient

# Инициализация компонентов
embedder = Embedder(model_name=config.embeddings.model)
vector_store = VectorStore(
    persist_directory=config.vectordb.persist_directory,
    collection_name=config.vectordb.collection_name,
)

llm_client = YandexGPTClient(
    api_key=config.llm.api_key,
    folder_id=config.llm.folder_id,
    model=config.llm.model,
)

# Создание RAG pipeline
rag_pipeline = RAGPipeline(
    llm_client=llm_client,
    embedder=embedder,
    vector_store=vector_store,
    top_k=5,
)

# Задать вопрос
result = rag_pipeline.answer_question("Как оформить отпуск?")

print("Ответ:", result["answer"])
print("\nИсточники:")
for source in result["sources"]:
    print(f"- {source['metadata']['file_name']}")
```

### Индексация документов программно

```python
from pathlib import Path
from src.parsers import BaseParser
from src.embeddings import Embedder, TextSplitter, VectorStore

# Инициализация
embedder = Embedder()
vector_store = VectorStore()
text_splitter = TextSplitter(chunk_size=500, chunk_overlap=100)

# Обработка документа
doc_path = Path("data/raw/document.pdf")
parser = BaseParser.get_parser(doc_path, extract_tables=True)
documents = parser.parse(doc_path)

# Разбиение на чанки
doc_dicts = [{"text": doc.text, "metadata": doc.metadata} for doc in documents]
chunks = text_splitter.split_documents(doc_dicts)

# Генерация эмбеддингов
texts = [chunk["text"] for chunk in chunks]
metadatas = [chunk["metadata"] for chunk in chunks]
embeddings = embedder.embed_texts(texts)

# Добавление в векторное хранилище
vector_store.add_documents(
    texts=texts,
    embeddings=embeddings.tolist(),
    metadatas=metadatas,
)
```

## Интеграция с другими системами

### REST API (FastAPI пример)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag import RAGPipeline

app = FastAPI()

# Инициализация RAG pipeline (один раз при старте)
rag_pipeline = initialize_rag_pipeline()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list
    num_sources: int

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        result = rag_pipeline.answer_question(request.question)
        return AnswerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Запуск: uvicorn api:app --reload
```

### Telegram Bot пример

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Инициализация RAG pipeline
rag_pipeline = initialize_rag_pipeline()

async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Я бот для ответов на вопросы по документам. Задайте вопрос!"
    )

async def handle_question(update: Update, context):
    question = update.message.text
    result = rag_pipeline.answer_question(question)

    answer = result["answer"]
    sources = "\n".join([
        f"• {s['metadata']['file_name']}"
        for s in result["sources"][:3]
    ])

    response = f"{answer}\n\nИсточники:\n{sources}"
    await update.message.reply_text(response)

# Настройка бота
app = Application.builder().token("YOUR_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
app.run_polling()
```

## Настройка для различных сценариев

### Сценарий 1: Высокая точность

```yaml
# configs/config.yaml
retrieval:
  top_k: 10
  relevance_threshold: 0.85
  rerank: true

llm:
  temperature: 0.1
```

### Сценарий 2: Быстрый ответ

```yaml
# configs/config.yaml
retrieval:
  top_k: 3
  relevance_threshold: 0.6
  rerank: false

llm:
  model: "yandexgpt-lite"
  temperature: 0.3
```

### Сценарий 3: Большой контекст

```yaml
# configs/config.yaml
embeddings:
  chunk_size: 1000
  chunk_overlap: 200

retrieval:
  top_k: 7
  relevance_threshold: 0.7
```

## Мониторинг и логирование

### Включение детального логирования

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ]
)
```

### Метрики производительности

```python
import time

def measure_query_time(rag_pipeline, question):
    start_time = time.time()
    result = rag_pipeline.answer_question(question)
    end_time = time.time()

    print(f"Время ответа: {end_time - start_time:.2f} сек")
    print(f"Найдено источников: {result['num_sources']}")

    return result
```

## Troubleshooting

### Проблема: Нет релевантных документов

```python
# Понизьте порог релевантности
rag_pipeline.relevance_threshold = 0.5

# Увеличьте количество документов
rag_pipeline.top_k = 10
```

### Проблема: Медленная генерация эмбеддингов

```python
# Увеличьте batch size
embedder = Embedder(batch_size=64)

# Или используйте более легкую модель
embedder = Embedder(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
```

### Проблема: Ошибки парсинга PDF

```python
# Включите OCR для сканированных документов
# Установите: pip install pytesseract pdf2image
# Обновите PDFParser для использования OCR
```
