import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://hhtracker:hhtracker@localhost:5432/hhtracker",
)
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "1")
