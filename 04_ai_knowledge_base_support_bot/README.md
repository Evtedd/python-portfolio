AI Knowledge Base Support Bot
AI сервис поддержки по базе знаний. Приложение принимает документы, разбивает текст на фрагменты, строит эмбеддинги, ищет релевантный контекст и формирует ответ через OpenAI compatible LLM провайдер или локальный fallback.
Возможности
* Загрузка документов в форматах PDF, TXT и MD.
* Извлечение текста из документов.
* Разбиение текста на чанки с overlap.
* Генерация embeddings через заменяемый провайдер.
* Локальный hash провайдер для демо без API ключа.
* Поиск релевантных чанков по cosine similarity.
* Ответы через FastAPI.
* Telegram интерфейс для вопросов.
* Хранение документов, чанков и истории ответов.
* Удаление документов из базы знаний.
Стек
* Python
* FastAPI
* aiogram 3
* SQLAlchemy 2
* SQLite / PostgreSQL
* pypdf
* httpx
* OpenAI compatible API
* Docker / Docker Compose
* pytest / pytest asyncio
Архитектура
app/
├── api/                   # FastAPI endpoints
├── bot/                   # Telegram-интерфейс
├── db/                    # подключение к базе данных
├── embeddings/            # providers для эмбеддингов
├── ingestion/             # парсинг файлов и чанкинг
├── llm/                   # prompt и LLM-провайдеры
├── retrieval/             # поиск по векторам
├── models.py              # SQLAlchemy-модели
├── repository.py          # работа с БД
└── services.py            # основная бизнес-логика RAG
```

API
| Метод | Endpoint | Описание |
| | | |
| `POST` | `/documents` | загрузить документ |
| `GET` | `/documents` | список документов |
| `DELETE` | `/documents/{document_id}` | удалить документ |
| `POST` | `/ask` | задать вопрос по базе знаний |

Переменные окружения
DATABASE_URL=sqlite+aiosqlite:///./knowledge.db
TELEGRAM_BOT_TOKEN=
EMBEDDINGS_PROVIDER=hash
EMBEDDINGS_BASE_URL=https://api.openai.com/v1
EMBEDDINGS_API_KEY=
EMBEDDINGS_MODEL=text-embedding-3-small
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
CHUNK_SIZE=900
CHUNK_OVERLAP=120
TOP_K=4
```

Для PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://knowledge:knowledge@postgres:5432/knowledge
```

Локальный запуск API

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8001
```

Локальный запуск Telegram бота

```bash
python -m app.bot.main
```

Запуск через Docker

```bash
docker compose up --build
```

API будет доступен на:

http://localhost:8001
```

Примеры запросов

Загрузка документа:

```bash
curl -F "file=@manual.pdf" http://localhost:8001/documents
```

Вопрос по базе знаний:

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Какие условия возврата?"}'
```

Тесты

```bash
pytest
```


