Real Time Market Analytics
Сервис принимает поток рыночных тиков, нормализует сообщения, строит OHLCV свечи, сохраняет данные и отдаёт live обновления через WebSocket. Для локального демо есть симулятор котировок, поэтому проект можно запускать без подключения к бирже.
Проект демонстрирует обработку stream данных, агрегацию временных рядов, live dashboard, WebSocket API и правила алертов
Возможности
* Генератор fake market ticks для локального демо.
* Binance WebSocket client для реального потока.
* Нормализация входящих сообщений.
* Агрегация тиков в OHLCV свечи.
* Несколько окон агрегации, например 60 и 300 секунд.
* Хранение тиков, свечей и алертов.
* In memory pub/sub bus с ограничением очереди.
* Ценовые алерты `price_gt` и `price_lt`.
* REST API для symbols и candles.
* WebSocket endpoint для live ticks/candles/alerts.
* Простой dashboard с live графиком.
* Docker Compose с TimescaleDB и Redis как инфраструктурной заготовкой.
Стек
* Python
* FastAPI
* WebSockets
* SQLAlchemy 2
* SQLite / PostgreSQL / TimescaleDB compatible connection
* Docker / Docker Compose
* pytest / pytest asyncio
Архитектура
app/
├── alerts/                # правила ценовых алертов
├── api/                   # REST, WebSocket и dashboard
├── bus/                   # in-memory pub/sub
├── dashboard/             # HTML dashboard
├── db/                    # подключение к базе данных
├── ingest/                # симулятор и Binance client
├── processing/            # normalizer и OHLCV aggregator
├── storage/               # сохранение тиков, свечей и алертов
├── domain.py              # доменные модели
├── models.py              # SQLAlchemy-модели
├── schemas.py             # Pydantic-схемы
└── service.py             # orchestration обработки потока
API
| Метод | Endpoint | Описание |
| | | |
| `GET` | `/symbols` | список инструментов |
| `GET` | `/candles/{symbol}` | исторические свечи |
| `WS` | `/ws/{symbol}` | live ticks, candles и alerts |

 Переменные окружения

DATABASE_URL=sqlite+aiosqlite:///./market.db
SYMBOLS=BTCUSDT,ETHUSDT
WINDOWS=60,300
SIMULATION_MODE=true
EXCHANGE_WS_URL=wss://stream.binance.com:9443/ws
QUEUE_MAX_SIZE=5000
PRICE_ALERTS=BTCUSDT:price_gt:70000,ETHUSDT:price_lt:2000
TICK_INTERVAL_SECONDS=1
```
`WINDOWS` задаёт размеры свечей в секундах. `PRICE_ALERTS` принимает правила формата

```text
SYMBOL:price_gt:VALUE
SYMBOL:price_lt:VALUE
```

Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8005
```

## Запуск через Docker

```bash
docker compose up --build
```

API будет доступен на:

```text
http://localhost:8005
```

Dashboard:

```text
http://localhost:8005/dashboard
```

## Режим симуляции

По умолчанию:

```env
SIMULATION_MODE=true
```

В этом режиме сервис генерирует fake ticks для выбранных symbols.

Режим реального потока

```env
SIMULATION_MODE=false
SYMBOLS=BTCUSDT,ETHUSDT
```

После этого ingest клиент использует WebSocket URL биржи.

Пример WebSocket

```text
ws://localhost:8005/ws/BTCUSDT
```

Тесты

```bash
pytest
```
Что демонстрирует проект
* Stream processing.
* Агрегацию тиков в OHLCV.
* WebSocket API.
* Live dashboard.
* Правила алертов.
* Разделение ingest, processing, storage и API.
* Тестирование normalizer, aggregator и alerts.
