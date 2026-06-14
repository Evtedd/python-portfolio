FastAPI Helpdesk CRM Backend
REST API для helpdesk/CRM системы заявок. Пользователи могут регистрироваться, создавать обращения, оставлять комментарии и отслеживать статусы. Администратор может просматривать пользователей и управлять заявками.
Возможности
* Регистрация пользователей.
* Авторизация через JWT.
* Роли `user` и `admin`.
* Создание заявок.
* Просмотр списка заявок.
* Фильтрация заявок по статусу и автору.
* Пагинация через `limit` и `offset`.
* Просмотр одной заявки с комментариями.
* Добавление комментариев.
* Обновление заявки.
* Смена статуса заявки администратором.
* Просмотр списка пользователей только для администратора.
* Автоматическая Swagger документация. Стек

* Python
* FastAPI
* SQLAlchemy 2
* PostgreSQL
* Alembic
* JWT
* passlib / bcrypt
* Pydantic
* Docker / Docker Compose
* pytest

Архитектура
app/
├── main.py                # FastAPI-приложение
├── api/                   # роуты auth, tickets, users
├── core/                  # конфиг, безопасность, зависимости
├── db/                    # подключение к БД
├── models/                # SQLAlchemy ORM-модели
├── schemas/               # Pydantic-схемы
└── services/              # бизнес-логика пользователей и заявок
API
| Метод | Endpoint | Описание |
| | | |
| `POST` | `/auth/register` | регистрация пользователя |
| `POST` | `/auth/login` | получение JWT токена |
| `GET` | `/users` | список пользователей, только admin |
| `POST` | `/tickets` | создать заявку |
| `GET` | `/tickets` | список заявок с фильтрами |
| `GET` | `/tickets/{ticket_id}` | получить заявку |
| `PATCH` | `/tickets/{ticket_id}` | обновить заявку |
| `POST` | `/tickets/{ticket_id}/comments` | добавить комментарий |
Переменные окружения

```env
DATABASE_URL=postgresql+psycopg://helpdesk:helpdesk@postgres:5432/helpdesk
SECRET_KEY=change_me_to_long_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
 Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Запуск через Docker

```bash
docker compose up --build
```

API будет доступен на:

```text
http://localhost:8000
```

Пример запроса

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","full_name":"Test User"}'
```
Тесты

```bash
pytest
```

