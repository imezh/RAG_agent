# Document QA Agent

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-FF4B4B.svg)](https://streamlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Система ответов на вопросы по внутренним нормативным документам организации с использованием RAG (Retrieval-Augmented Generation).

## Возможности

- Парсинг документов в форматах PDF, DOCX, Markdown, TXT
- Извлечение и обработка таблиц из документов
- Семантический поиск по документам с использованием векторных эмбеддингов
- Ответы на вопросы с использованием YandexGPT или GigaChat
- Веб-интерфейс на базе Streamlit
- Указание источников в ответах
- Поддержка русского языка

## Архитектура

```
doc-qa-agent/
├── src/
│   ├── parsers/          # Парсеры документов
│   ├── embeddings/       # Эмбеддинги и векторное хранилище
│   ├── rag/             # RAG pipeline и LLM клиенты
│   └── config.py        # Управление конфигурацией
├── configs/
│   └── config.yaml      # Конфигурационный файл
├── data/
│   ├── raw/            # Исходные документы
│   ├── processed/      # Обработанные документы
│   └── vectordb/       # База векторных эмбеддингов
├── app.py              # Streamlit веб-приложение
└── index_documents.py  # Скрипт индексации документов
```

## Установка

### 1. Клонируйте репозиторий

```bash
git clone <repository-url>
cd doc-qa-agent
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Скопируйте `.env.example` в `.env` и заполните учетные данные:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
# Для YandexGPT
YANDEX_API_KEY=your_yandex_api_key_here
YANDEX_FOLDER_ID=your_folder_id_here

# Или для GigaChat
GIGACHAT_API_KEY=your_gigachat_api_key_here
```

### 5. (Опционально) Настройте конфигурацию

Отредактируйте `configs/config.yaml` для изменения параметров системы.

## Использование

### Индексация документов

Перед использованием системы необходимо проиндексировать документы:

```bash
# Индексировать документы из директории
python index_documents.py ./data/raw

# Очистить существующий индекс и создать новый
python index_documents.py ./data/raw --clear
```

### Запуск веб-интерфейса

```bash
streamlit run app.py
```

Приложение будет доступно по адресу `http://localhost:8501`

### Использование через веб-интерфейс

1. Откройте веб-интерфейс
2. Нажмите "Инициализировать систему" в боковой панели
3. Загрузите документы через форму загрузки или используйте предварительно проиндексированные
4. Задавайте вопросы в чате
5. Система предоставит ответы с указанием источников

## Конфигурация

### Основные параметры

Файл `configs/config.yaml`:

```yaml
# LLM настройки
llm:
  provider: "yandexgpt"  # yandexgpt или gigachat
  model: "yandexgpt-lite"
  temperature: 0.3
  max_tokens: 2000

# Эмбеддинги
embeddings:
  model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  chunk_size: 500
  chunk_overlap: 100

# Поиск
retrieval:
  top_k: 5
  relevance_threshold: 0.7
```

### Поддерживаемые LLM провайдеры

1. **YandexGPT**
   - Модели: `yandexgpt-lite`, `yandexgpt`
   - Требуется API ключ и Folder ID

2. **GigaChat**
   - Модель: `GigaChat`
   - Требуется API ключ

### Поддерживаемые форматы документов

- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`)
- Markdown (`.md`)
- Текстовые файлы (`.txt`)

## Расширенные возможности

### Извлечение таблиц

Для улучшенного извлечения таблиц из PDF можно установить дополнительные библиотеки:

```bash
pip install camelot-py[cv]
# или
pip install tabula-py
```

И обновить метод `_extract_tables_from_page` в `src/parsers/pdf_parser.py`

### Добавление новых форматов

1. Создайте новый парсер в `src/parsers/`
2. Унаследуйте от `BaseParser`
3. Реализуйте метод `parse()`
4. Добавьте в `BaseParser.get_parser()`

### Использование других векторных БД

Система поддерживает ChromaDB по умолчанию. Для использования FAISS:

```python
# В src/embeddings/vector_store.py
# Создайте новый класс FAISSVectorStore
```

## Тестирование

```bash
# Запустить все тесты
pytest

# Запустить с покрытием
pytest --cov=src tests/
```

## Производительность

### Рекомендации по оптимизации

1. **Размер чанков**: Уменьшите `chunk_size` для более точного поиска, увеличьте для лучшего контекста
2. **Top-K**: Увеличьте для большего контекста, уменьшите для скорости
3. **Порог релевантности**: Увеличьте для более строгого фильтра
4. **Batch size**: Увеличьте для ускорения генерации эмбеддингов

### Примерная производительность

- Индексация: ~10-50 документов/мин (зависит от размера)
- Ответ на вопрос: ~3-10 секунд
- Поиск: <1 секунда

## Решение проблем

### Ошибка инициализации

- Проверьте правильность API ключей в `.env`
- Убедитесь, что все зависимости установлены

### Плохое качество ответов

- Увеличьте `top_k` для большего контекста
- Уменьшите `relevance_threshold`
- Проверьте качество исходных документов
- Попробуйте другую модель эмбеддингов

### Медленная работа

- Уменьшите `top_k`
- Используйте `yandexgpt-lite` вместо `yandexgpt`
- Увеличьте `batch_size` для эмбеддингов

## Безопасность

- Храните `.env` в секрете (добавлен в `.gitignore`)
- Не коммитьте API ключи
- Регулярно обновляйте зависимости
- Используйте HTTPS для продакшена

## Лицензия

MIT License

## Авторы

Создано с использованием:
- Python 3.8+
- Streamlit
- ChromaDB
- Sentence Transformers
- YandexGPT / GigaChat

## Поддержка

Для вопросов и предложений создавайте issue в репозитории.
