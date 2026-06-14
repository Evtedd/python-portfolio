AI Resume & Vacancy Matcher
Сервис сравнивает резюме с вакансией, рассчитывает match score, показывает совпавшие и недостающие навыки, генерирует черновик сопроводительного письма и сохраняет историю анализов.
Вакансию можно передать текстом, ссылкой на `hh.ru/vacancy/...` или ID вакансии HeadHunter. Резюме можно загрузить файлом или передать текстом.
 Возможности

* Загрузка резюме в PDF/TXT.
* Анализ текста резюме.
* Получение вакансии по ссылке или ID HeadHunter.
* Ручная вставка текста вакансии.
* Сравнение навыков кандидата и требований вакансии.
* Match score от 0 до 100.
* Список совпавших навыков.
* Список недостающих навыков.
* Генерация сопроводительного письма.
* Локальная эвристика без LLM API ключа.
* OpenAI compatible LLM провайдер при наличии ключа.
* История анализов.
* Статистика по откликам.
* Streamlit UI для демо.

Стек
* Python
* FastAPI
* Streamlit
* SQLAlchemy 2
* PostgreSQL / SQLite
* Alembic
* httpx
* pypdf
* OpenAI compatible API
* Docker / Docker Compose
* pytest
 Архитектура
```text
app/
├── api/                   # FastAPI endpoints
├── db/                    # подключение к базе данных
├── hh/                    # клиент HeadHunter API
├── llm/                   # LLM-клиент, prompts и fallback
├── parsing/               # парсинг резюме и вакансий
├── ui/                    # Streamlit-интерфейс
├── models.py              # SQLAlchemy-модели
├── repository.py          # хранение матчей и статусов
├── schemas.py             # Pydantic-схемы
└── services.py            # логика сравнения резюме и вакансии
```
API
| Метод | Endpoint | Описание |
| | | |
| `POST` | `/match` | сравнить резюме и вакансию |
| `GET` | `/matches` | история анализов |
| `POST` | `/matches/{match_id}/applications/{application_status}` | отметить статус отклика |
| `GET` | `/stats` | статистика по анализам и откликам |
Документация API после запуска:

```text
http://localhost:8002/docs
```

Streamlit UI:

```text
http://localhost:8501
```
Переменные окружения
```env
DATABASE_URL=sqlite:///./matcher.db
HH_BASE_URL=https://api.hh.ru
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
API_URL=http://localhost:8000
```
Для PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://matcher:matcher@postgres:5432/matcher
```
 Локальный запуск API
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.api.main:app --reload --port 8002
``
Локальный запуск UI

```bash
streamlit run app/ui/streamlit_app.py
```

Запуск через Docker
```bash
docker compose up --build
```
Пример сценария
1. Пользователь загружает резюме.
2. Вставляет ссылку на вакансию HeadHunter.
3. Сервис получает текст вакансии.
4. Сравнивает навыки и требования.
5. Возвращает score, объяснение и черновик сопроводительного письма.
6. Пользователь сохраняет статус: `applied`, `ignored`, `later`.
Тесты
```bash
pytest
```
Что демонстрирует проект
* Интеграцию с внешним API.
* Анализ текста резюме и вакансий.
* LLM assisted анализ.
* Fallback логику без внешних ключей.
* Backend + UI в одном проекте.
* Хранение истории и статусов.
* Тестирование парсинга и LLM ответов.

