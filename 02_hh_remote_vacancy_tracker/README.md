HH Remote Vacancy Tracker
Сервис для мониторинга удалённых Python вакансий на HeadHunter. Приложение периодически получает вакансии через API, фильтрует неподходящие варианты, сохраняет результат в базу данных и отправляет новые подходящие вакансии в Telegram.
Возможности
* Поиск вакансий через HeadHunter API.
* Фильтр удалённых вакансий.
* Whitelist/blacklist по ключевым словам.
* Сохранение вакансий в PostgreSQL.
* Защита от повторной отправки одной и той же вакансии.
* Telegram уведомления о новых вакансиях.
* Inline кнопки для смены статуса вакансии.
* Статусы: `new`, `applied`, `ignored`, `later`.
* Команда `/stats` для просмотра статистики.
* Периодический запуск по расписанию.

Стек

* Python
* httpx
* aiogram 3
* SQLAlchemy 2
* PostgreSQL
* Alembic
* Docker / Docker Compose
* pytest / pytest asyncio

 Архитектура
app/
├── main.py                # запуск сервиса
├── bot.py                 # Telegram-команды и callback-обработчики
├── config.py              # настройки приложения
├── filters.py             # whitelist/blacklist и проверка удалёнки
├── scheduler.py           # периодический опрос HH API
├── telegram.py            # отправка уведомлений в Telegram
├── repository.py          # сохранение вакансий и статистики
├── hh_client/             # async-клиент HeadHunter API
├── models/                # SQLAlchemy-модели
└── db/                    # подключение к базе данных
```

 Логика фильтрации
Сервис проверяет вакансию по нескольким условиям:

1. Вакансия должна подходить под удалённый формат.
2. Текст вакансии должен содержать хотя бы одно слово из whitelist.
3. Текст вакансии не должен содержать слова из blacklist.
4. Уже отправленные вакансии не отправляются повторно.

Пример whitelist:

```text
Python, FastAPI, Django, backend, junior, стажёр, удалённо
```

Пример blacklist:

преподаватель, учитель, продажи, офис, не IT


Переменные окружения
env
DATABASE_URL=postgresql+asyncpg://hhtracker:hhtracker@postgres:5432/hhtracker
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=123456789
HH_TEXT=Python backend
HH_AREA=113
HH_PER_PAGE=50
POLL_INTERVAL_SECONDS=900
WHITELIST_KEYWORDS=Python,FastAPI,Django,backend,стажер,стажёр,junior,удаленно,удалённо
BLACKLIST_KEYWORDS=преподаватель,учитель,продажи,не IT,офис
HTTP_TIMEOUT_SECONDS=20


Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

 Запуск через Docker

```bash
docker compose up --build
```

Миграции

```bash
alembic upgrade head
```

Тесты

```bash
pytest
```

