Multi Agent AI Orchestrator
Платформа для запуска задач через граф AI агентов: `planner → executor → critic`. Planner строит план, executor выполняет шаги и вызывает инструменты, critic проверяет результат и при необходимости запускает доработку.
Проект показывает архитектуру AI agent системы: состояние выполнения, трассировка шагов, registry инструментов, память, LLM провайдеры, API и streaming событий.
 Возможности
* Создание run задачи через API.
* Planner строит пошаговый план.
* Executor выполняет шаги и вызывает tools.
* Critic проверяет результат.
* Ограничение количества шагов.
* Ограничение количества ревизий.
* История запусков.
* Трассировка событий.
* SSE stream для live просмотра выполнения.
* Общая memory store.
* Fake LLM provider для тестов и локального демо.
* OpenAI compatible provider для внешних моделей.
* Расширяемый registry инструментов.
Стек
* Python
* FastAPI
* SQLAlchemy 2
* SQLite / PostgreSQL
* httpx
* Server Sent Events
* OpenAI compatible API
* Docker / Docker Compose
* pytest / pytest asyncio
Архитектура
```text
app/
├── agents/                # planner, executor, critic
├── api/                   # REST API и SSE stream
├── core/                  # состояние и цикл выполнения
├── db/                    # подключение к базе данных
├── llm/                   # fake и OpenAI-compatible providers
├── memory/                # простая общая память
├── tools/                 # registry и реализации инструментов
├── models.py              # SQLAlchemy-модели run/event
├── repository.py          # работа с историей запусков
└── schemas.py             # Pydantic-схемы
Инструменты
По умолчанию подключены:

| Tool | Назначение |
| | |
| `python_code` | запуск небольшого Python кода в subprocess с timeout |
| `http_request` | простой HTTP запрос |
| `memory_save` | сохранение факта в память |
| `web_search` | демо заготовка поисковой заметки |

Чтобы добавить новый инструмент, нужно создать класс с полями `name`, `description`, `args_model` и методом `run`, затем зарегистрировать его в `tools/defaults.py`.
API
| Метод | Endpoint | Описание |
| | | |
| `POST` | `/runs` | создать новый запуск |
| `GET` | `/runs/{run_id}` | получить запуск и события |
| `GET` | `/runs/{run_id}/stream` | stream событий выполнения |


## Переменные окружения

```env
DATABASE_URL=sqlite+aiosqlite:///./orchestrator.db
LLM_PROVIDER=fake
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
MAX_STEPS=12
MAX_REVISIONS=2
TOOL_TIMEOUT_SECONDS=5
```

Для внешнего LLM провайдера:

```env
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8004
```

## Запуск через Docker

```bash
docker compose up --build
```

API будет доступен на:

```text
http://localhost:8004
```

## Пример запроса

```bash
curl -X POST http://localhost:8004/runs \
  -H "Content-Type: application/json" \
  -d '{"goal":"calculate a tiny result", "max_steps":5}'
```

Получение результата:
```bash
curl http://localhost:8004/runs/1
```

Live stream:

```bash
curl http://localhost:8004/runs/1/stream
```
Тесты
```bash
pytest
```

Что демонстрирует проект
* Проектирование agentic workflow.
* Разделение ролей planner/executor/critic.
* Tool calling через registry.
* Трассировку выполнения.
* SSE для live событий.
* Абстракцию LLM провайдеров.
* Тестирование engine и registry.


