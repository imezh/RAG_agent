# Deployment Guide

## Развертывание на Render

### Автоматическое развертывание с Blueprint

1. **Fork или клонируйте репозиторий** на GitHub

2. **Подключите репозиторий к Render:**
   - Зайдите на [Render Dashboard](https://dashboard.render.com/)
   - Нажмите "New" → "Blueprint"
   - Выберите репозиторий `imezh/RAG_agent`
   - Render автоматически обнаружит `render.yaml`

3. **Настройте переменные окружения:**

   В Render Dashboard установите следующие environment variables:

   ```
   YANDEX_API_KEY=ваш_ключ_yandex
   YANDEX_FOLDER_ID=ваш_folder_id
   ```

   ИЛИ для GigaChat:

   ```
   GIGACHAT_API_KEY=ваш_ключ_gigachat
   ```

4. **Деплой:**
   - Нажмите "Apply"
   - Render автоматически развернет приложение
   - После завершения получите URL: `https://document-qa-agent.onrender.com`

### Ручное развертывание

1. **Создайте новый Web Service:**
   - Dashboard → "New" → "Web Service"
   - Подключите GitHub репозиторий

2. **Настройте параметры:**
   ```
   Name: document-qa-agent
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Добавьте переменные окружения** (см. выше)

4. **Добавьте Persistent Disk** (опционально):
   - Name: document-qa-data
   - Mount Path: /opt/render/project/src/data
   - Size: 1 GB (для free tier)

### Важные замечания

#### Free Tier ограничения:
- Сервис засыпает после 15 минут неактивности
- Холодный старт занимает ~30-60 секунд
- 750 часов в месяц бесплатно
- 512 MB RAM

#### Рекомендации для production:

1. **Используйте Starter план** ($7/мес):
   - Не засыпает
   - Больше RAM
   - Лучшая производительность

2. **Оптимизируйте зависимости:**
   ```bash
   # Используйте более легкие альтернативы
   pip install sentence-transformers --no-deps
   ```

3. **Настройте кэширование:**
   - Используйте Render's Persistent Disk для ChromaDB
   - Кэшируйте модели эмбеддингов

4. **Мониторинг:**
   - Проверяйте логи в Render Dashboard
   - Настройте alerts для ошибок

### Переменные окружения

#### Обязательные:

Для YandexGPT:
```
YANDEX_API_KEY=<your-api-key>
YANDEX_FOLDER_ID=<your-folder-id>
```

Для GigaChat:
```
GIGACHAT_API_KEY=<your-api-key>
```

#### Опциональные:

```
PYTHON_VERSION=3.11.0
```

### Проблемы и решения

#### 1. Приложение не запускается

**Проблема:** Ошибка импорта модулей

**Решение:**
```bash
# Проверьте логи в Render Dashboard
# Убедитесь, что все зависимости в requirements.txt
```

#### 2. ChromaDB ошибки

**Проблема:** Нет доступа к файловой системе

**Решение:**
- Добавьте Persistent Disk
- Или используйте in-memory режим для тестирования

#### 3. Медленная загрузка моделей

**Проблема:** Модели загружаются при каждом запросе

**Решение:**
```python
# В app.py используйте st.cache_resource
@st.cache_resource
def load_embedder():
    return Embedder()
```

#### 4. Out of Memory

**Проблема:** 512MB недостаточно

**Решение:**
- Обновитесь до Starter плана
- Используйте более легкую модель эмбеддингов:
  ```yaml
  embeddings:
    model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  ```

### Альтернативные платформы

#### Streamlit Cloud (Рекомендуется для Streamlit)
- Бесплатный tier специально для Streamlit
- Проще в настройке
- https://streamlit.io/cloud

#### Heroku
```bash
# Добавьте Procfile
web: streamlit run app.py --server.port=$PORT
```

#### Railway
- Похож на Render
- Хорошая бесплатная квота
- https://railway.app

#### Google Cloud Run
- Pay-as-you-go
- Автоматическое масштабирование
- Требует Docker

### Docker деплой

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Затем:
```bash
docker build -t doc-qa-agent .
docker run -p 8501:8501 doc-qa-agent
```

## Обновление приложения

### Автоматическое (через Git):
```bash
git push origin main
# Render автоматически пересоберет и задеплоит
```

### Ручное:
- Render Dashboard → Your Service → "Manual Deploy" → "Deploy latest commit"

## Мониторинг

### Логи:
```bash
# В Render Dashboard → Logs
# Или через CLI:
render logs -s document-qa-agent
```

### Метрики:
- CPU usage
- Memory usage
- Response times
- Error rates

Все доступно в Render Dashboard → Metrics

## Стоимость

### Free Tier:
- 750 часов/месяц
- 512 MB RAM
- Сервис засыпает
- **$0/месяц**

### Starter:
- Не засыпает
- 512 MB RAM
- **$7/месяц**

### Standard:
- 2 GB RAM
- Лучшая производительность
- **$25/месяц**

## Поддержка

При проблемах с деплоем:
1. Проверьте [Render документацию](https://render.com/docs)
2. Создайте issue в репозитории
3. Проверьте логи в Dashboard
