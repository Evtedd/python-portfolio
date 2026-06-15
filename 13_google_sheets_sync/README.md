Автономная работа с Google Таблицами
Сервис синхронизирует строки Google Sheets с внутренней БД по декларативному конфигу, ведет журнал запусков, не падает на одной битой строке и умеет работать в fake режиме без доступа к Google.
Что внутри
* клиент Google Sheets за интерфейсом
* fake клиент in memory для тестов и демо
* нормализация и валидация строк
* идемпотентное сохранение по ключевой колонке
* история запусков и audit log изменений
* health endpoint и ручной запуск задач
* опциональные алерты в Telegram
 Конфиг задач

```env
SYNC_TASKS_JSON=[{"name":"products","spreadsheet_id":"demo","range_name":"products!A:Z","table_name":"products","key_column":"sku","columns":{"sku":"sku","name":"name","price":"price"},"bidirectional":false}]
```

Переменные окружения

```env
DATABASE_URL=postgresql+asyncpg://sheets_sync:sheets_sync@postgres:5432/sheets_sync
GOOGLE_FAKE_MODE=true
GOOGLE_CREDENTIALS_PATH=
GOOGLE_CREDENTIALS_JSON=
ALERT_TELEGRAM_TOKEN=
ALERT_TELEGRAM_CHAT_ID=
SYNC_INTERVAL_SECONDS=300
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

Ручной запуск:

```bash
curl -X POST http://localhost:8013/sync
```
