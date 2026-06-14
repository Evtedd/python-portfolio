import aiosqlite
import json
import time
import uuid
from config import DB_PATH, SUPER_ADMIN_ID


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT,
                source TEXT,
                first_seen_at REAL,
                last_seen_at REAL,
                total_starts INTEGER DEFAULT 0,
                current_status TEXT DEFAULT 'new',
                attempts_count INTEGER DEFAULT 0,
                is_blocked INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS admins (
                telegram_user_id INTEGER PRIMARY KEY,
                role TEXT DEFAULT 'admin',
                added_by INTEGER,
                added_at REAL
            );

            CREATE TABLE IF NOT EXISTS test_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                started_at REAL,
                finished_at REAL,
                current_question TEXT,
                total_score INTEGER DEFAULT 0,
                result_status TEXT DEFAULT 'in_progress',
                grant_reason TEXT,
                deny_reason TEXT,
                access_given INTEGER DEFAULT 0,
                access_given_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(telegram_user_id)
            );

            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                question_key TEXT,
                answer_index INTEGER,
                answer_value TEXT,
                is_correct INTEGER,
                points INTEGER DEFAULT 0,
                answered_at REAL,
                FOREIGN KEY (session_id) REFERENCES test_sessions(session_id)
            );

            CREATE TABLE IF NOT EXISTS events_log (
                event_id TEXT PRIMARY KEY,
                user_id INTEGER,
                admin_id INTEGER,
                event_type TEXT,
                payload_json TEXT,
                created_at REAL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)

        # Убедиться, что super admin в таблице admins
        await db.execute(
            "INSERT OR IGNORE INTO admins (telegram_user_id, role, added_by, added_at) VALUES (?, 'super_admin', ?, ?)",
            (SUPER_ADMIN_ID, SUPER_ADMIN_ID, time.time()),
        )

        # Дефолтные настройки
        from config import CHANNEL_LINK, CHAT_LINK
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('channel_link', ?)", (CHANNEL_LINK,))
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('chat_link', ?)", (CHAT_LINK,))
        await db.commit()


# Настройки
async def get_setting(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else default


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()


# Логирование
async def log_event(user_id: int, event_type: str, payload: dict = None, admin_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO events_log (event_id, user_id, admin_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, admin_id, event_type, json.dumps(payload or {}, ensure_ascii=False), time.time()),
        )
        await db.commit()


# Пользователи
async def upsert_user(user) -> dict:
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        row = await db.execute_fetchall(
            "SELECT * FROM users WHERE telegram_user_id = ?", (user.id,)
        )
        if row:
            await db.execute(
                """UPDATE users SET username=?, first_name=?, last_name=?, language_code=?,
                   last_seen_at=?, total_starts=total_starts+1 WHERE telegram_user_id=?""",
                (user.username, user.first_name, user.last_name, user.language_code, now, user.id),
            )
        else:
            await db.execute(
                """INSERT INTO users (telegram_user_id, username, first_name, last_name,
                   language_code, first_seen_at, last_seen_at, total_starts)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                (user.id, user.username, user.first_name, user.last_name, user.language_code, now, now),
            )
        await db.commit()
    return await get_user(user.id)


async def update_user_source(user_id: int, source: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET source=? WHERE telegram_user_id=?", (source, user_id))
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def update_user_status(user_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET current_status=? WHERE telegram_user_id=?", (status, user_id))
        await db.commit()


async def set_user_blocked(user_id: int, blocked: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_blocked=? WHERE telegram_user_id=?", (1 if blocked else 0, user_id))
        await db.commit()


async def get_users_paginated(offset: int = 0, limit: int = 10, search: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if search:
            q = """SELECT * FROM users WHERE
                   CAST(telegram_user_id AS TEXT) LIKE ? OR
                   username LIKE ? OR first_name LIKE ? OR last_name LIKE ?
                   ORDER BY last_seen_at DESC LIMIT ? OFFSET ?"""
            s = f"%{search}%"
            rows = await db.execute_fetchall(q, (s, s, s, s, limit, offset))
            count_q = """SELECT COUNT(*) FROM users WHERE
                        CAST(telegram_user_id AS TEXT) LIKE ? OR
                        username LIKE ? OR first_name LIKE ? OR last_name LIKE ?"""
            async with db.execute(count_q, (s, s, s, s)) as cur:
                total = (await cur.fetchone())[0]
        else:
            rows = await db.execute_fetchall(
                "SELECT * FROM users ORDER BY last_seen_at DESC LIMIT ? OFFSET ?", (limit, offset)
            )
            async with db.execute("SELECT COUNT(*) FROM users") as cur:
                total = (await cur.fetchone())[0]
        return [dict(r) for r in rows], total


# Тестовые сессии
async def create_session(user_id: int) -> str:
    sid = str(uuid.uuid4())[:12]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO test_sessions (session_id, user_id, started_at, current_question) VALUES (?, ?, ?, 'q1')",
            (sid, user_id, time.time()),
        )
        await db.execute(
            "UPDATE users SET attempts_count = attempts_count + 1 WHERE telegram_user_id=?",
            (user_id,),
        )
        await db.commit()
    return sid


async def get_active_session(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM test_sessions WHERE user_id=? AND result_status='in_progress' ORDER BY started_at DESC LIMIT 1",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_last_session(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM test_sessions WHERE user_id=? ORDER BY started_at DESC LIMIT 1",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_all_sessions(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(
            "SELECT * FROM test_sessions WHERE user_id=? ORDER BY started_at DESC", (user_id,)
        )
        return [dict(r) for r in rows]


async def update_session(session_id: str, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [session_id]
        await db.execute(f"UPDATE test_sessions SET {sets} WHERE session_id=?", vals)
        await db.commit()


# Ответы
async def save_answer(session_id: str, question_key: str, answer_index: int, answer_value: str, is_correct: bool, points: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO answers (session_id, question_key, answer_index, answer_value, is_correct, points, answered_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, question_key, answer_index, answer_value, int(is_correct), points, time.time()),
        )
        await db.commit()


async def get_session_answers(session_id: str) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(
            "SELECT * FROM answers WHERE session_id=? ORDER BY answered_at", (session_id,)
        )
        return [dict(r) for r in rows]


# Админы
async def is_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM admins WHERE telegram_user_id=?", (user_id,)) as cur:
            return await cur.fetchone() is not None


async def is_super_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM admins WHERE telegram_user_id=? AND role='super_admin'", (user_id,)
        ) as cur:
            return await cur.fetchone() is not None


async def add_admin(user_id: int, added_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO admins (telegram_user_id, role, added_by, added_at) VALUES (?, 'admin', ?, ?)",
            (user_id, added_by, time.time()),
        )
        await db.commit()


async def remove_admin(user_id: int) -> bool:
    if user_id == SUPER_ADMIN_ID:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE telegram_user_id=? AND role != 'super_admin'", (user_id,))
        await db.commit()
    return True


async def get_all_admins() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall("SELECT * FROM admins ORDER BY added_at")
        return [dict(r) for r in rows]


# Статистика
async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}

        async with db.execute("SELECT COUNT(*) FROM users") as c:
            stats["total_users"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM test_sessions") as c:
            stats["total_sessions"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM test_sessions") as c:
            stats["users_started"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM test_sessions WHERE result_status != 'in_progress'") as c:
            stats["tests_completed"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM test_sessions WHERE result_status='passed'") as c:
            stats["users_passed"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM test_sessions WHERE result_status='failed'") as c:
            stats["users_failed"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM test_sessions WHERE result_status='in_progress'") as c:
            stats["tests_in_progress"] = (await c.fetchone())[0]

        async with db.execute("SELECT AVG(total_score) FROM test_sessions WHERE result_status != 'in_progress'") as c:
            val = (await c.fetchone())[0]
            stats["avg_score"] = round(val, 1) if val else 0

        async with db.execute("SELECT COUNT(*) FROM test_sessions WHERE access_given=1") as c:
            stats["access_granted_total"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM test_sessions WHERE access_given=1 AND grant_reason='auto'") as c:
            stats["access_granted_auto"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM test_sessions WHERE access_given=1 AND grant_reason='manual'") as c:
            stats["access_granted_manual"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM test_sessions WHERE access_given=0 AND result_status='failed'") as c:
            stats["access_denied"] = (await c.fetchone())[0]

        if stats["total_users"] > 0:
            stats["conversion"] = round(stats["users_passed"] / stats["total_users"] * 100, 1)
        else:
            stats["conversion"] = 0

        return stats


# Логи
async def get_logs_paginated(offset: int = 0, limit: int = 15, user_id: int = None) -> tuple:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if user_id:
            rows = await db.execute_fetchall(
                "SELECT * FROM events_log WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset),
            )
            async with db.execute("SELECT COUNT(*) FROM events_log WHERE user_id=?", (user_id,)) as c:
                total = (await c.fetchone())[0]
        else:
            rows = await db.execute_fetchall(
                "SELECT * FROM events_log ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset)
            )
            async with db.execute("SELECT COUNT(*) FROM events_log") as c:
                total = (await c.fetchone())[0]
        return [dict(r) for r in rows], total


# Ручное управление
async def grant_access_manually(user_id: int, admin_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        # Найти или создать сессию
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT session_id FROM test_sessions WHERE user_id=? ORDER BY started_at DESC LIMIT 1",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()

        if row:
            sid = row["session_id"]
            await db.execute(
                """UPDATE test_sessions SET result_status='passed', access_given=1,
                   access_given_at=?, grant_reason='manual' WHERE session_id=?""",
                (time.time(), sid),
            )
        else:
            sid = str(uuid.uuid4())[:12]
            await db.execute(
                """INSERT INTO test_sessions
                   (session_id, user_id, started_at, finished_at, result_status, grant_reason, access_given, access_given_at)
                   VALUES (?, ?, ?, ?, 'passed', 'manual', 1, ?)""",
                (sid, user_id, time.time(), time.time(), time.time()),
            )

        await db.execute("UPDATE users SET current_status='granted_manually' WHERE telegram_user_id=?", (user_id,))
        await db.commit()


async def deny_access_manually(user_id: int, admin_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET current_status='denied_manually' WHERE telegram_user_id=?", (user_id,)
        )
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT session_id FROM test_sessions WHERE user_id=? ORDER BY started_at DESC LIMIT 1",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
        if row:
            await db.execute(
                """UPDATE test_sessions SET result_status='failed', access_given=0,
                   deny_reason='denied_by_admin' WHERE session_id=?""",
                (row["session_id"],),
            )
        await db.commit()


async def reset_user_attempt(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET current_status='new', attempts_count=0, is_blocked=0 WHERE telegram_user_id=?",
            (user_id,),
        )
        await db.execute(
            "DELETE FROM test_sessions WHERE user_id=?", (user_id,)
        )
        await db.execute(
            "DELETE FROM answers WHERE session_id IN (SELECT session_id FROM test_sessions WHERE user_id=?)",
            (user_id,),
        )
        await db.commit()


# Источники трафика
async def get_source_stats() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall("""
            SELECT u.source,
                   COUNT(DISTINCT u.telegram_user_id) as total,
                   COUNT(DISTINCT CASE WHEN ts.result_status='passed' THEN u.telegram_user_id END) as passed
            FROM users u
            LEFT JOIN test_sessions ts ON u.telegram_user_id = ts.user_id
            WHERE u.source IS NOT NULL AND u.source != ''
            GROUP BY u.source
            ORDER BY total DESC
        """)
        return [dict(r) for r in rows]
