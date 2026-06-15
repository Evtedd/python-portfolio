Портфолио проектов
Pet-проекты (Python / FastAPI / AI)

| # | Проект | Что делает | Стек |
|---|--------|------------|------|
| 1 | **Telegram Task Manager Bot** | Бот-менеджер задач: дедлайны, напоминания, статусы, категории, статистика, экспорт в CSV | aiogram 3, SQLAlchemy 2 (async), APScheduler-логика на asyncio, SQLite/PostgreSQL, Docker |
| 2 | **HH Remote Vacancy Tracker** | Ищет удалённые Python-вакансии через API HeadHunter, фильтрует по white/blacklist и шлёт подходящие в Telegram | httpx (async), SQLAlchemy 2, PostgreSQL, aiogram, Docker |
| 3 | **FastAPI Helpdesk / CRM** | REST-бэкенд системы заявок: пользователи, JWT, роли, тикеты, комментарии, статусы, фильтры | FastAPI, SQLAlchemy 2, PostgreSQL, Alembic, JWT, Docker |
| 4 | **AI Knowledge Base Bot** | RAG-бот поддержки: отвечает на вопросы по загруженной базе знаний (PDF/txt/md) со ссылками на источники | FastAPI, aiogram, эмбеддинги + векторный поиск, LLM (OpenAI-совместимый), Docker |
| 5 | **AI Resume & Vacancy Matcher** | Сравнивает резюме с вакансией, считает % соответствия, находит недостающие навыки и пишет сопроводительное | FastAPI, HH API, LLM, PostgreSQL, Streamlit/HTML, Docker |
| 6 | **Multimodal Search Engine** | Семантический поиск по видео, аудио, PDF и изображениям одним текстовым запросом, с таймкодами и номерами страниц | FastAPI, faster-whisper, CLIP, pgvector/Qdrant, ffmpeg, фоновые воркеры, Docker |
| 7 | **Multi-agent AI Orchestrator** | Собственный мини-фреймворк агентов (planner → executor → critic) с инструментами, общей памятью и стримингом шагов | FastAPI, свой движок графа, LLM tool-calling, PostgreSQL, векторная память, Docker |
| 8 | **Real-time Market Analytics** | Приём биржевых котировок по WebSocket, потоковая агрегация в свечи/индикаторы, алерты и живой дашборд | asyncio, websockets, FastAPI WS, TimescaleDB/ClickHouse, Redis Streams, Docker |
| 9 | **Noir Maison Haute** | Интернет-магазин нишевой парфюмерии: каталог, корзина, многошаговое оформление с оплатой в крипте, личный кабинет, письма-подтверждения, уведомления в Telegram. Интерфейс на трёх языках (EN/RU/ES) | React 18 + Vite, Node.js/Express, better-sqlite3, nodemailer |
| 10 | **Бот приёма участников** | Telegram-бот для анкетирования и скрининга кандидатов: пошаговый опрос, админ-панель, статистика и логи | Python, python-telegram-bot, aiosqlite |
| 11 | **Авто-создание карточек Wildberries** | Собирает карточки товаров из CSV / Google Sheets / БД, валидирует данные, готовит медиа и отправляет батчами в WB Content API; режим DRY_RUN, идемпотентность по vendorCode, обработка лимитов API | FastAPI, SQLAlchemy 2 (async), PostgreSQL, Alembic, httpx, tenacity, Google Sheets API, Docker |
| 12 | **Авто-постинг новинок в Instagram и Pinterest** | Принимает новинки через webhook или из БД, формирует подпись и хэштеги, ставит публикации в очередь с расписанием и повторными попытками; единый интерфейс Publisher, дедуп по паре товар×площадка | FastAPI, SQLAlchemy 2 (async), PostgreSQL, httpx, Instagram Graph API, Pinterest API v5, Docker |
| 13 | **Sync с Google Таблицами** | Синхронизирует строки Google Sheets с БД по декларативному конфигу, ведёт журнал запусков и audit log, не падает на одной битой строке, умеет fake-режим без доступа к Google | FastAPI, SQLAlchemy 2 (async), PostgreSQL, APScheduler, Google Sheets API, Docker |
| 14 | **Self-hosted платформа автоматизации** | Запускает сценарии из триггеров (webhook / расписание / опрос API) и действий-коннекторов за единым интерфейсом; шаблоны данных между шагами, очередь в Redis, шифрование секретов, web-дашборд | FastAPI, SQLAlchemy 2 (async), PostgreSQL, Redis, APScheduler, cryptography (Fernet), Docker |
| 15 | **Робот поиска новинок Wildberries** | Периодически обходит публичные эндпоинты WB, применяет фильтры по цене/словам/продавцу, считает перспективность товара и шлёт находки в Telegram; клиент изолирован, режим симуляции | FastAPI, SQLAlchemy 2 (async), PostgreSQL, Alembic, httpx, aiogram 3, Docker |
