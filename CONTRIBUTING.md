# Contributing to Document QA Agent

Спасибо за ваш интерес к улучшению Document QA Agent! Мы приветствуем вклад от сообщества.

## Как внести вклад

### Сообщения об ошибках

Если вы нашли ошибку:

1. Проверьте, не была ли она уже зарегистрирована в [Issues](https://github.com/imezh/RAG_agent/issues)
2. Если нет, создайте новый issue с:
   - Четким описанием проблемы
   - Шагами для воспроизведения
   - Ожидаемым и фактическим поведением
   - Версией Python и зависимостей
   - Логами ошибок (если есть)

### Предложение новых функций

1. Создайте issue с меткой "enhancement"
2. Опишите предлагаемую функциональность
3. Объясните, почему это полезно
4. Подождите обсуждения перед началом работы

### Pull Requests

1. **Fork** репозитория
2. Создайте **новую ветку** от `main`:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Внесите изменения
4. Убедитесь, что код соответствует стилю:
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```
5. Добавьте тесты для новой функциональности
6. Запустите тесты:
   ```bash
   pytest tests/
   ```
7. Обновите документацию
8. Commit с осмысленным сообщением:
   ```bash
   git commit -m "Add: новая функция для извлечения таблиц"
   ```
9. Push в ваш fork:
   ```bash
   git push origin feature/amazing-feature
   ```
10. Создайте Pull Request

## Стиль кода

### Python

- Следуйте [PEP 8](https://pep8.org/)
- Используйте **Black** для форматирования (line length: 88)
- Используйте **flake8** для линтинга
- Используйте **mypy** для проверки типов
- Добавляйте docstrings для всех публичных функций и классов

Пример:

```python
def parse_document(file_path: Path) -> List[Document]:
    """
    Parse a document and extract text.

    Args:
        file_path: Path to the document file

    Returns:
        List of parsed Document objects

    Raises:
        ValueError: If file format is not supported
    """
    pass
```

### Commit сообщения

Используйте конвенцию [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - новая функциональность
- `fix:` - исправление ошибки
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг без изменения функциональности
- `test:` - добавление или изменение тестов
- `chore:` - изменения в процессе сборки или вспомогательных инструментах

Примеры:
```
feat: add support for Excel documents
fix: resolve PDF parsing error with tables
docs: update installation instructions
```

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src tests/

# Конкретный файл
pytest tests/test_parsers.py

# С выводом
pytest -v
```

### Написание тестов

- Создайте тесты в `tests/`
- Используйте pytest
- Стремитесь к покрытию >80%
- Тестируйте граничные случаи

## Структура проекта

```
doc-qa-agent/
├── src/               # Исходный код
│   ├── parsers/      # Парсеры документов
│   ├── embeddings/   # Эмбеддинги
│   └── rag/         # RAG pipeline
├── tests/            # Тесты
├── configs/          # Конфигурация
└── docs/            # Документация
```

## Требования к окружению

- Python 3.8+
- Все зависимости из `requirements.txt`
- Pre-commit hooks (рекомендуется)

## Pre-commit hooks

Установите pre-commit hooks для автоматической проверки:

```bash
pip install pre-commit
pre-commit install
```

Создайте `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
```

## Документация

При добавлении новой функциональности:

1. Обновите `README.md`
2. Добавьте примеры в `USAGE_EXAMPLES.md`
3. Обновите `CHANGELOG.md`
4. Добавьте docstrings в код

## Лицензия

Отправляя Pull Request, вы соглашаетесь лицензировать ваш вклад под MIT License.

## Вопросы?

Если у вас есть вопросы, создайте issue или напишите в discussions.

## Благодарности

Спасибо всем, кто вносит вклад в развитие проекта!
