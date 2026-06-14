# Multimodal Search Engine
Сервис индексирует PDF, аудио, видео и изображения, после чего позволяет искать по ним обычным текстовым запросом. Проект демонстрирует обработку разных типов файлов, разбиение текста на сегменты, embeddings, similarity search и чат по найденным источникам.
В лёгком режиме проект работает без GPU и внешних моделей: embeddings строятся детерминированным hash провайдером, а транскрипция медиа берётся из sidecar файла вроде `video.mp4.txt` или из имени файла. Внешние embeddings и LLM можно подключить через переменные окружения.
 Возможности
* Загрузка PDF, аудио, видео и изображений.
* Извлечение текста из PDF.
* Поддержка sidecar транскриптов для аудио и видео.
* Разбиение текста на чанки с overlap.
* Индексация сегментов.
* Поиск по cosine similarity.
* Чат поверх найденных источников.
* Локальный hash embeddings provider для демо.
* OpenAI compatible LLM provider.
* Background worker для индексации.
* Inline worker для простого локального запуска.
* Docker Compose с PostgreSQL и Qdrant заготовкой.

Поддерживаемые форматы
.pdf, .mp3, .wav, .m4a, .mp4, .mov, .mkv, .png, .jpg, .jpeg, .webp
```

Стек

* Python
* FastAPI
* SQLAlchemy 2
* SQLite / PostgreSQL
* pypdf
* httpx
* OpenAI compatible API
* Docker / Docker Compose
* pytest / pytest asyncio

Архитектура

```text
app/
├── api/                   # загрузка файлов, поиск и чат
├── chunking/              # разбиение текста на чанки
├── db/                    # подключение к базе данных
├── embeddings/            # providers для эмбеддингов
├── ingestion/             # извлечение текста из файлов
├── llm/                   # генерация ответа по найденным источникам
├── search/                # similarity search
├── transcription/         # provider транскрипции
├── vectorstore/           # математика векторного поиска
├── workers/               # фоновая индексация
├── models.py              # SQLAlchemy-модели
├── repository.py          # работа с БД
└── schemas.py             # Pydantic-схемы
```

API
| Метод | Endpoint | Описание |
| | | |
| `POST` | `/assets` | загрузить файл |
| `GET` | `/assets` | список загруженных файлов |
| `POST` | `/search` | найти релевантные фрагменты |
| `POST` | `/chat` | получить ответ по найденным источникам |

Переменные окружения
DATABASE_URL=sqlite+aiosqlite:///./multimodal.db
STORAGE_DIR=./storage
MAX_UPLOAD_MB=200
TEXT_EMBEDDINGS_PROVIDER=hash
IMAGE_EMBEDDINGS_PROVIDER=hash
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
ENABLE_TRANSCRIPTION=false
ENABLE_INLINE_WORKER=true
WORKER_POLL_SECONDS=2
CHUNK_WORDS=180
CHUNK_OVERLAP=30
SEARCH_TOP_K=8

Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8003
```

Запуск отдельного 

```bash
ENABLE_INLINE_WORKER=false python -m app.workers.main
```
Запуск через Docker

```bash
docker compose up --build
```


Что демонстрирует проект

* Обработку мультимодальных данных.
* Построение поискового индекса.
* Similarity search.
* Background workers.
* API для загрузки и поиска.
* LLM интеграцию поверх найденных источников.
* Проектирование расширяемой архитектуры providers.

