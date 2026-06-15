Self hosted платформа автоматизации
Платформа запускает сценарии из триггеров и действий: webhook, расписание, опрос API, HTTP запросы, Telegram, email, запись в БД и тестовые коннекторы.
Архитектура
* triggers принимают событие и выбирают flow
* core рендерит шаблоны и передает данные между шагами
* connectors выполняют действия за единым интерфейсом
* queue кладет тяжелые запуски в Redis
* repository хранит flow, runs и журнал шагов
* web dashboard показывает список сценариев и позволяет запускать их вручную
Переменные окружения

```env
DATABASE_URL=postgresql+asyncpg://automation:automation@postgres:5432/automation
REDIS_URL=redis://redis:6379/0
API_KEY=change-me
FERNET_KEY=
FAKE_MODE=true
```

`FERNET_KEY` можно создать командой:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Пример сценария

```json
{
  "name": "new-product",
  "enabled": true,
  "trigger": {"type": "webhook", "key": "new-product"},
  "steps": [
    {"name": "post", "connector": "memory", "settings": {}, "input": {"text": "Новый товар {{event.name}}"}},
    {"name": "save", "connector": "db_log", "settings": {}, "input": {"message": "{{post.text}}"}}
  ]
}
```

Запуск

```bash
pip install -r requirements.txt
uvicorn app.api.main:app --reload
```

Через Docker:

```bash
docker compose up --build
```
