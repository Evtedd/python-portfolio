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
| Noir Maison Haute | Интернет-магазин нишевой парфюмерии: каталог, корзина, многошаговое оформление с оплатой в крипте, личный кабинет, письма-подтверждения, уведомления в Telegram. Интерфейс на трёх языках (EN/RU/ES) | React 18 + Vite, Node.js/Express, better-sqlite3, nodemailer |
| Бот приёма участников | Telegram-бот для анкетирования и скрининга кандидатов: пошаговый опрос, админ-панель, статистика и логи | Python, python-telegram-bot, aiosqlite |