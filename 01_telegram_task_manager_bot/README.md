Telegram Task Manager Bot
Telegram бот для управления личными задачами: добавление задач, дедлайны, категории, статусы, поиск, недельная статистика и экспорт в CSV.
Возможности
* Добавление задач через команду /add.
* Просмотр задач через /list.
* Поиск задач через /search.
* Недельная статистика через /stats.
* Экспорт задач в CSV через /export.
* Категории задач через #category.
* Дедлайны в формате YYYY MM DD или YYYY MM DDTHH:MM.
* Статусы задач: `new`, in_progress, done.
* Inline кнопки для смены статуса.
* Фоновые напоминания перед дедлайном.
* Админ команды /admin_users и /admin_stats.
* SQLite для локального запуска и PostgreSQL через DATABASE_URL.

Стек
* Python
* aiogram 3
* asyncio
* SQLAlchemy 2
* SQLite / PostgreSQL
* Alembic
* Docker / Docker Compose
* pytest / pytest asyncio

Архитектура
app/
├── bot.py                 # точка входа Telegram-бота
├── config.py              # настройки через переменные окружения
├── scheduler.py           # фоновый цикл напоминаний
├── db/                    # подключение к базе данных
├── handlers/              # Telegram-команды и callback-обработчики
├── keyboards/             # inline кнопки
├── models/                # SQLAlchemy-модели
├── repositories/          # работа с данными
└── services/              # бизнес логика задач и парсинг сообщений


Команды бота

| Команда | Назначение |
| | |
| `/start` | приветствие и краткая справка |
| `/add` | добавить задачу |
| `/list` | показать список задач |
| `/search` | найти задачи по тексту |
| `/stats` | показать статистику за неделю |
| `/export` | выгрузить задачи в CSV |
| `/admin_users` | список пользователей для администратора |
| `/admin_stats` | общая статистика для администратора |

Пример использования

/add Сделать README для портфолио #portfolio 2026-06-20T18:00
/list
/stats
/export
Переменные окружения

env
BOT_TOKEN=
DATABASE_URL=sqlite+aiosqlite:///./tasks.db
ADMIN_IDS=123456789,987654321
REMINDER_MINUTES_BEFORE=30
REMINDER_POLL_SECONDS=60
Для PostgreSQL:
env
DATABASE_URL=postgresql+asyncpg://taskbot:taskbot@postgres:5432/taskbot

Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.bot
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
