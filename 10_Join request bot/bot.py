import logging
import time
from datetime import datetime, timezone, timedelta

MSK = timezone(timedelta(hours=3))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

import database as db
from config import (
    BOT_TOKEN, SUPER_ADMIN_ID, QUESTIONS, QUESTION_ORDER,
    PASS_SCORE, MAX_SCORE, MAX_ATTEMPTS, DOT,
    INTRO_TEXT, SUCCESS_TEXT, FAIL_TEXT, FAIL_TEXT_RETRY,
    ALREADY_PASSED_TEXT, NO_RETAKES_TEXT, BLOCKED_TEXT,
    ADMIN_CONTACTS,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# Утилиты

def ts_to_str(ts):
    if not ts:
        return "нет"
    return datetime.fromtimestamp(ts, tz=MSK).strftime("%d.%m.%Y %H:%M")


def ts_short(ts):
    if not ts:
        return "нет"
    return datetime.fromtimestamp(ts, tz=MSK).strftime("%d.%m %H:%M")


def contact_buttons() -> list:
    """Кнопки для связи с админами."""
    return [InlineKeyboardButton(label, url=url) for label, url in ADMIN_CONTACTS]


async def get_links() -> tuple[str, str]:
    """Получить текущие ссылки из БД."""
    ch = await db.get_setting("channel_link", "")
    ct = await db.get_setting("chat_link", "")
    return ch, ct


async def access_buttons() -> list:
    """Кнопки входа в канал и чат."""
    ch, ct = await get_links()
    return [
        [InlineKeyboardButton("Войти в канал", url=ch)],
        [InlineKeyboardButton("Войти в чат", url=ct)],
    ]


async def delete_prev(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Удалить предыдущее сообщение бота."""
    prev = context.user_data.get("last_bot_msg")
    if prev:
        try:
            await context.bot.delete_message(chat_id, prev)
        except Exception:
            pass
        context.user_data["last_bot_msg"] = None


async def send(update: Update, context: ContextTypes.DEFAULT_TYPE,
               text: str, reply_markup=None, delete_user_msg=True):
    """Отправить сообщение, удалив предыдущее."""
    chat_id = update.effective_chat.id
    await delete_prev(context, chat_id)

    # Удалить сообщение пользователя (/start и т.д.)
    if delete_user_msg and update.message:
        try:
            await update.message.delete()
        except Exception:
            pass

    msg = await context.bot.send_message(
        chat_id, text, parse_mode=ParseMode.HTML, reply_markup=reply_markup,
    )
    context.user_data["last_bot_msg"] = msg.message_id
    return msg


def get_next_question(current_q: str, answers_so_far: dict) -> str | None:
    """Определяет следующий вопрос после текущего."""
    idx = QUESTION_ORDER.index(current_q) if current_q in QUESTION_ORDER else -1

    # После q5 проверяем, нужен ли q5_1
    if current_q == "q5":
        # Ответ "Высокий"  значит индекс 2
        q5_answer = answers_so_far.get("q5")
        if q5_answer is not None and q5_answer == 2:
            return "q5_1"
        else:
            return "q6"

    if current_q == "q5_1":
        return "q6"

    # Обычный порядок
    if idx < len(QUESTION_ORDER) - 1:
        return QUESTION_ORDER[idx + 1]

    return None  # Тест завершён


def build_question_keyboard(question_key: str) -> InlineKeyboardMarkup:
    q = QUESTIONS[question_key]
    buttons = []
    for i, opt in enumerate(q["options"]):
        buttons.append([InlineKeyboardButton(opt, callback_data=f"a:{question_key}:{i}")])
    return InlineKeyboardMarkup(buttons)


def user_display_name(user_data: dict) -> str:
    parts = []
    if user_data.get("first_name"):
        parts.append(user_data["first_name"])
    if user_data.get("last_name"):
        parts.append(user_data["last_name"])
    name = " ".join(parts) or "Без имени"
    uname = f"@{user_data['username']}" if user_data.get("username") else ""
    return f"{name} {uname}".strip()


# /start точка входа

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.upsert_user(user)

    # Источник трафика
    if context.args:
        source = context.args[0]
        await db.update_user_source(user.id, source)
        await db.log_event(user.id, "start_with_source", {"source": source})

    await db.log_event(user.id, "bot_start")

    is_adm = await db.is_admin(user.id)

    # Проверяем текущее состояние пользователя
    status = user_data["current_status"]

    # Уже прошёл тест или получил доступ вручную
    if status in ("passed", "granted_manually"):
        buttons = await access_buttons()
        if is_adm:
            buttons.append([InlineKeyboardButton("Админ панель", callback_data="ap")])
        await send(update, context, ALREADY_PASSED_TEXT,
                   reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Заблокирован
    if user_data["is_blocked"]:
        buttons = [contact_buttons()]
        if is_adm:
            buttons.append([InlineKeyboardButton("Админ панель", callback_data="ap")])
        await send(update, context, BLOCKED_TEXT,
                   reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Отклонён вручную
    if status == "denied_manually":
        buttons = [contact_buttons()]
        if is_adm:
            buttons.append([InlineKeyboardButton("Админ панель", callback_data="ap")])
        await send(update, context, NO_RETAKES_TEXT,
                   reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Провалил и попытки кончились
    if status == "failed" and user_data["attempts_count"] >= MAX_ATTEMPTS:
        buttons = [contact_buttons()]
        if is_adm:
            buttons.append([InlineKeyboardButton("Админ панель", callback_data="ap")])
        await send(update, context, NO_RETAKES_TEXT,
                   reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Есть незавершённая сессия  продолжить
    active = await db.get_active_session(user.id)
    if active:
        await db.log_event(user.id, "resumed_session")
        q_key = active["current_question"]
        q = QUESTIONS.get(q_key)
        if q:
            await send(update, context, q["text"],
                       reply_markup=build_question_keyboard(q_key))
            return

    # Первый вход или повторная попытка
    name = user.first_name or "друг"
    buttons = [[InlineKeyboardButton("Начать", callback_data="st")]]
    if is_adm:
        buttons.append([InlineKeyboardButton("Админ панель", callback_data="ap")])

    await send(update, context, INTRO_TEXT.format(name=name),
               reply_markup=InlineKeyboardMarkup(buttons))


# Начало теста

async def cb_start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    user_data = await db.get_user(user.id)
    if not user_data:
        user_data = await db.upsert_user(user)

    # Проверка допуска
    if user_data["current_status"] in ("passed", "granted_manually"):
        await query.edit_message_text(ALREADY_PASSED_TEXT, parse_mode=ParseMode.HTML)
        return

    if user_data["is_blocked"]:
        await query.edit_message_text(BLOCKED_TEXT, parse_mode=ParseMode.HTML)
        return

    if user_data["attempts_count"] >= MAX_ATTEMPTS:
        await query.edit_message_text(NO_RETAKES_TEXT, parse_mode=ParseMode.HTML)
        return

    # Создаём сессию
    sid = await db.create_session(user.id)
    await db.update_user_status(user.id, "in_progress")
    await db.log_event(user.id, "test_started", {"session_id": sid})

    # Показываем первый вопрос
    first_q = QUESTION_ORDER[0]
    await db.update_session(sid, current_question=first_q)
    await db.log_event(user.id, "question_shown", {"question": first_q})

    q = QUESTIONS[first_q]
    await query.edit_message_text(
        q["text"], parse_mode=ParseMode.HTML,
        reply_markup=build_question_keyboard(first_q),
    )


# Обработка ответов

async def cb_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    # Парсим callback
    parts = query.data.split(":")
    if len(parts) != 3:
        return
    _, q_key, ans_idx_str = parts
    ans_idx = int(ans_idx_str)

    # Проверяем активную сессию
    session = await db.get_active_session(user.id)
    if not session:
        await query.edit_message_text(
            "<blockquote>Нет активного теста. Нажмите /start</blockquote>",
            parse_mode=ParseMode.HTML,
        )
        return

    sid = session["session_id"]

    # Проверяем, что отвечают на текущий вопрос
    if session["current_question"] != q_key:
        return

    q = QUESTIONS[q_key]
    answer_text = q["options"][ans_idx]
    is_correct = q["correct"] is not None and ans_idx == q["correct"]
    points = q["points"] if is_correct else 0

    # Сохраняем ответ
    await db.save_answer(sid, q_key, ans_idx, answer_text, is_correct, points)
    await db.log_event(user.id, "answer_given", {
        "session_id": sid, "question": q_key,
        "answer": answer_text, "correct": is_correct, "points": points,
    })

    # Обновляем баллы
    new_score = session["total_score"] + points
    await db.update_session(sid, total_score=new_score)

    # Собираем ответы для определения следующего вопроса
    all_answers = await db.get_session_answers(sid)
    answers_map = {a["question_key"]: a["answer_index"] for a in all_answers}

    next_q = get_next_question(q_key, answers_map)

    if next_q:
        # Следующий вопрос
        await db.update_session(sid, current_question=next_q)
        await db.log_event(user.id, "question_shown", {"question": next_q})
        nq = QUESTIONS[next_q]
        await query.edit_message_text(
            nq["text"], parse_mode=ParseMode.HTML,
            reply_markup=build_question_keyboard(next_q),
        )
    else:
        # Тест завершён  считаем результат
        await finish_test(query, user, sid, new_score, answers_map)


async def finish_test(query, user, session_id: str, score: int, answers_map: dict):
    """Подводим итоги теста."""
    await db.log_event(user.id, "test_completed", {"session_id": session_id, "score": score})

    # Проверяем критичные вопросы (q1 и q2  оба должны быть верными)
    q1_correct = answers_map.get("q1") == QUESTIONS["q1"]["correct"]
    q2_correct = answers_map.get("q2") == QUESTIONS["q2"]["correct"]

    deny_reasons = []
    if score < PASS_SCORE:
        deny_reasons.append("Недостаточно баллов")
    if not q1_correct:
        deny_reasons.append("Не пройден критичный вопрос 1")
    if not q2_correct:
        deny_reasons.append("Не пройден критичный вопрос 2")

    passed = len(deny_reasons) == 0

    if passed:
        await db.update_session(
            session_id,
            finished_at=time.time(),
            result_status="passed",
            grant_reason="auto",
            access_given=1,
            access_given_at=time.time(),
        )
        await db.update_user_status(user.id, "passed")
        await db.log_event(user.id, "access_granted_auto", {"score": score})

        buttons = await access_buttons()
        await query.edit_message_text(
            SUCCESS_TEXT, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        deny_str = "; ".join(deny_reasons)
        await db.update_session(
            session_id,
            finished_at=time.time(),
            result_status="failed",
            deny_reason=deny_str,
            access_given=0,
        )
        await db.update_user_status(user.id, "failed")
        await db.log_event(user.id, "access_denied", {"score": score, "reasons": deny_reasons})

        user_data = await db.get_user(user.id)
        if user_data["attempts_count"] < MAX_ATTEMPTS:
            buttons = [
                [InlineKeyboardButton("Попробовать ещё раз", callback_data="st")],
                contact_buttons(),
            ]
            await query.edit_message_text(
                FAIL_TEXT_RETRY, parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            buttons = [contact_buttons()]
            await query.edit_message_text(
                FAIL_TEXT, parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons),
            )


# АДМИН ПАНЕл

async def admin_check(query) -> bool:
    if not await db.is_admin(query.from_user.id):
        await query.answer("Нет доступа", show_alert=True)
        return False
    return True


def admin_main_keyboard(is_super: bool) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Статистика", callback_data="as")],
        [InlineKeyboardButton("Пользователи", callback_data="au:0")],
        [InlineKeyboardButton("Логи", callback_data="al:0")],
        [InlineKeyboardButton("Источники трафика", callback_data="asrc")],
    ]
    if is_super:
        buttons.append([InlineKeyboardButton("Управление админами", callback_data="ala")])
        buttons.append([InlineKeyboardButton("Настройки ссылок", callback_data="aset")])
    return InlineKeyboardMarkup(buttons)


async def cb_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    is_super = await db.is_super_admin(query.from_user.id)
    await query.edit_message_text(
        "<blockquote><b>Админ панель</b></blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard(is_super),
    )


# Статистика

async def cb_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    s = await db.get_stats()
    text = (
        "<blockquote>"
        f"<b>Статистика</b>\n\n"
        f"{DOT} Всего пользователей: <b>{s['total_users']}</b>\n"
        f"{DOT} Начали тест: <b>{s['users_started']}</b>\n"
        f"{DOT} Завершили тест: <b>{s['tests_completed']}</b>\n"
        f"{DOT} Тест не закончили: <b>{s['tests_in_progress']}</b>\n"
        f"{DOT} Получили доступ: <b>{s['users_passed']}</b>\n"
        f"{DOT} Не получили доступ: <b>{s['users_failed']}</b>\n"
        f"{DOT} Средний балл: <b>{s['avg_score']}</b>\n"
        f"{DOT} Конверсия: <b>{s['conversion']}%</b>\n\n"
        f"<b>Доступ</b>\n"
        f"{DOT} Выдано всего: <b>{s['access_granted_total']}</b>\n"
        f"{DOT} Автоматически: <b>{s['access_granted_auto']}</b>\n"
        f"{DOT} Вручную: <b>{s['access_granted_manual']}</b>\n"
        f"{DOT} Отказано: <b>{s['access_denied']}</b>\n\n"
        "</blockquote>"
    )
    buttons = [[InlineKeyboardButton("Назад", callback_data="ap")]]
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


# Источники трафика

async def cb_admin_sources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    sources = await db.get_source_stats()
    if not sources:
        text = "<blockquote><b>Источники трафика</b>\n\nДанных пока нет.</blockquote>"
    else:
        lines = ["<blockquote><b>Источники трафика</b>\n"]
        for s in sources:
            conv = round(s["passed"] / s["total"] * 100, 1) if s["total"] else 0
            lines.append(f"{DOT} <code>{s['source']}</code>: {s['total']} чел., прошли: {s['passed']} ({conv}%)")
        lines.append("</blockquote>")
        text = "\n".join(lines)

    buttons = [[InlineKeyboardButton("Назад", callback_data="ap")]]
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


# Пользователи

async def cb_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    parts = query.data.split(":")
    page = int(parts[1]) if len(parts) > 1 else 0
    per_page = 8

    # Поиск
    search = context.user_data.get("admin_search")
    users, total = await db.get_users_paginated(page * per_page, per_page, search)

    if not users:
        text = "<blockquote><b>Пользователи</b>\n\nНикого не найдено.</blockquote>"
    else:
        lines = [f"<blockquote><b>Пользователи</b>  ({total} всего)\n"]
        if search:
            lines.append(f"Поиск: <code>{search}</code>\n")
        for u in users:
            name = user_display_name(u)
            status_icon = {
                "passed": "[ OK ]",
                "failed": "[FAIL]",
                "in_progress": "[ .. ]",
                "granted_manually": "[M OK]",
                "denied_manually": "[M NO]",
                "new": "[ .. ]",
            }.get(u["current_status"], "[ ? ]")
            lines.append(f"<code>{status_icon}</code> {name}  /  <code>{u['telegram_user_id']}</code>")
        lines.append("</blockquote>")
        text = "\n".join(lines)

    buttons = []
    # Пользователи как кнопки для детализации
    for u in users:
        label = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() or str(u['telegram_user_id'])
        buttons.append([InlineKeyboardButton(
            f"{label}  |  {u['current_status']}",
            callback_data=f"ad:{u['telegram_user_id']}",
        )])

    # Пагинация
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("< Назад", callback_data=f"au:{page - 1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton("Далее >", callback_data=f"au:{page + 1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("Поиск", callback_data="aus")])
    buttons.append([InlineKeyboardButton("Сбросить поиск", callback_data="auc")])
    buttons.append([InlineKeyboardButton("Назад", callback_data="ap")])

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


async def cb_admin_user_search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return
    context.user_data["awaiting_search"] = True
    await query.edit_message_text(
        "<blockquote>Введите user_id, username или имя для поиска:</blockquote>",
        parse_mode=ParseMode.HTML,
    )


async def cb_admin_user_search_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("admin_search", None)
    # Перенаправляем на список
    query.data = "au:0"
    await cb_admin_users(update, context)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений для поиска в админке."""
    if context.user_data.get("awaiting_search"):
        context.user_data["awaiting_search"] = False
        context.user_data["admin_search"] = update.message.text.strip()
        # Показываем результат
        users, total = await db.get_users_paginated(0, 8, context.user_data["admin_search"])
        search = context.user_data["admin_search"]

        if not users:
            text = f"<blockquote>Поиск: <code>{search}</code>\n\nНикого не найдено.</blockquote>"
        else:
            lines = [f"<blockquote><b>Результаты поиска</b>: <code>{search}</code>  ({total})\n"]
            for u in users:
                name = user_display_name(u)
                lines.append(f"{DOT} {name}  |  <code>{u['telegram_user_id']}</code>  |  {u['current_status']}")
            lines.append("</blockquote>")
            text = "\n".join(lines)

        buttons = []
        for u in users:
            label = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() or str(u['telegram_user_id'])
            buttons.append([InlineKeyboardButton(
                f"{label}  |  {u['current_status']}",
                callback_data=f"ad:{u['telegram_user_id']}",
            )])
        buttons.append([InlineKeyboardButton("Сбросить поиск", callback_data="auc")])
        buttons.append([InlineKeyboardButton("Назад", callback_data="ap")])

        await send(update, context, text, reply_markup=InlineKeyboardMarkup(buttons))

    elif context.user_data.get("awaiting_addadmin"):
        context.user_data["awaiting_addadmin"] = False
        text = update.message.text.strip()
        try:
            new_admin_id = int(text)
        except ValueError:
            await send(update, context, "<blockquote>Неверный формат. Введите числовой user_id.</blockquote>")
            return
        await db.add_admin(new_admin_id, update.effective_user.id)
        await db.log_event(new_admin_id, "admin_added", {"by": update.effective_user.id}, admin_id=update.effective_user.id)
        await send(update, context,
            f"<blockquote>Админ <code>{new_admin_id}</code> добавлен.</blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="ala")]]),
        )

    elif context.user_data.get("awaiting_deladmin"):
        context.user_data["awaiting_deladmin"] = False
        text = update.message.text.strip()
        try:
            del_admin_id = int(text)
        except ValueError:
            await send(update, context, "<blockquote>Неверный формат. Введите числовой user_id.</blockquote>")
            return
        if del_admin_id == SUPER_ADMIN_ID:
            await send(update, context, "<blockquote>Нельзя удалить super admin.</blockquote>")
            return
        ok = await db.remove_admin(del_admin_id)
        if ok:
            await db.log_event(del_admin_id, "admin_removed", {"by": update.effective_user.id}, admin_id=update.effective_user.id)
        await send(update, context,
            f"<blockquote>Админ <code>{del_admin_id}</code> удалён.</blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="ala")]]),
        )

    elif context.user_data.get("awaiting_set_channel"):
        context.user_data["awaiting_set_channel"] = False
        new_link = update.message.text.strip()
        await db.set_setting("channel_link", new_link)
        await db.log_event(update.effective_user.id, "setting_changed",
                           {"key": "channel_link", "value": new_link},
                           admin_id=update.effective_user.id)
        await send(update, context,
            f"<blockquote>Ссылка на канал обновлена:\n<code>{new_link}</code></blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад к настройкам", callback_data="aset")]]),
        )

    elif context.user_data.get("awaiting_set_chat"):
        context.user_data["awaiting_set_chat"] = False
        new_link = update.message.text.strip()
        await db.set_setting("chat_link", new_link)
        await db.log_event(update.effective_user.id, "setting_changed",
                           {"key": "chat_link", "value": new_link},
                           admin_id=update.effective_user.id)
        await send(update, context,
            f"<blockquote>Ссылка на чат обновлена:\n<code>{new_link}</code></blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад к настройкам", callback_data="aset")]]),
        )


# Карточка пользователя

async def cb_admin_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    uid = int(query.data.split(":")[1])
    u = await db.get_user(uid)
    if not u:
        await query.edit_message_text("<blockquote>Пользователь не найден.</blockquote>", parse_mode=ParseMode.HTML)
        return

    sessions = await db.get_all_sessions(uid)
    last = sessions[0] if sessions else None

    # Ответы последней сессии
    answers_text = ""
    if last:
        answers = await db.get_session_answers(last["session_id"])
        ans_lines = []
        for a in answers:
            q_data = QUESTIONS.get(a["question_key"], {})
            correct_idx = q_data.get("correct")
            correct_mark = "+" if a["is_correct"] else "x"
            correct_answer = q_data["options"][correct_idx] if correct_idx is not None else "нет"
            ans_lines.append(
                f"  <b>{a['question_key']}</b>: {a['answer_value']}\n"
                f"  [{correct_mark}] Верный: {correct_answer}\n"
                f"  Баллы: {a['points']}"
            )
        answers_text = "\n\n".join(ans_lines)

    text = (
        "<blockquote>"
        f"<b>Карточка пользователя</b>\n\n"
        f"{DOT} ID: <code>{u['telegram_user_id']}</code>\n"
        f"{DOT} Username: {'@' + u['username'] if u.get('username') else 'нет'}\n"
        f"{DOT} Имя: {u.get('first_name', 'нет')}\n"
        f"{DOT} Фамилия: {u.get('last_name') or 'нет'}\n"
        f"{DOT} Язык: {u.get('language_code', 'нет')}\n"
        f"{DOT} Источник: {u.get('source') or 'нет'}\n"
        f"{DOT} Первый визит: {ts_to_str(u['first_seen_at'])}\n"
        f"{DOT} Последний визит: {ts_to_str(u['last_seen_at'])}\n"
        f"{DOT} Попыток: {u['attempts_count']}\n"
        f"{DOT} Статус: <b>{u['current_status']}</b>\n"
        f"{DOT} Заблокирован: {'Да' if u['is_blocked'] else 'Нет'}\n"
    )

    if last:
        text += (
            f"\n<b>Последняя сессия</b>\n"
            f"{DOT} Балл: <b>{last['total_score']} / {MAX_SCORE}</b>\n"
            f"{DOT} Результат: {last['result_status']}\n"
            f"{DOT} Доступ выдан: {'Да' if last['access_given'] else 'Нет'}\n"
            f"{DOT} Причина выдачи: {last.get('grant_reason') or 'нет'}\n"
            f"{DOT} Причина отказа: {last.get('deny_reason') or 'нет'}\n"
        )

    if answers_text:
        text += f"\n<b>Ответы</b>\n\n{answers_text}\n"

    text += "</blockquote>"

    buttons = [
        [
            InlineKeyboardButton("Выдать доступ", callback_data=f"ag:{uid}"),
            InlineKeyboardButton("Отказать", callback_data=f"an:{uid}"),
        ],
        [
            InlineKeyboardButton("Сбросить попытку", callback_data=f"ar:{uid}"),
            InlineKeyboardButton("Заблокировать", callback_data=f"ab:{uid}"),
        ],
        [InlineKeyboardButton("Логи пользователя", callback_data=f"aul:{uid}:0")],
        [InlineKeyboardButton("Назад к списку", callback_data="au:0")],
    ]

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


# Действия с пользователем

async def cb_admin_grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    uid = int(query.data.split(":")[1])
    await db.grant_access_manually(uid, query.from_user.id)
    await db.log_event(uid, "access_granted_manual", {"by": query.from_user.id}, admin_id=query.from_user.id)

    # Уведомляем пользователя
    try:
        buttons = await access_buttons()
        await context.bot.send_message(
            uid,
            "<blockquote>Доступ выдан администратором.</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception:
        pass

    await query.edit_message_text(
        f"<blockquote>Доступ для <code>{uid}</code> выдан вручную.</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"ad:{uid}")]]),
    )


async def cb_admin_deny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    uid = int(query.data.split(":")[1])
    await db.deny_access_manually(uid, query.from_user.id)
    await db.log_event(uid, "access_denied_manual", {"by": query.from_user.id}, admin_id=query.from_user.id)

    await query.edit_message_text(
        f"<blockquote>Доступ для <code>{uid}</code> отклонён.</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"ad:{uid}")]]),
    )


async def cb_admin_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    uid = int(query.data.split(":")[1])
    await db.reset_user_attempt(uid)
    await db.log_event(uid, "attempt_reset", {"by": query.from_user.id}, admin_id=query.from_user.id)

    await query.edit_message_text(
        f"<blockquote>Попытка для <code>{uid}</code> сброшена.\nПользователь может пройти тест заново.</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"ad:{uid}")]]),
    )


async def cb_admin_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    uid = int(query.data.split(":")[1])
    await db.set_user_blocked(uid, True)
    await db.log_event(uid, "user_blocked", {"by": query.from_user.id}, admin_id=query.from_user.id)

    await query.edit_message_text(
        f"<blockquote>Повторное прохождение для <code>{uid}</code> заблокировано.</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"ad:{uid}")]]),
    )


# Логи

EVENT_LABELS = {
    "bot_start": "Зашёл в бота",
    "start_with_source": "Зашёл по ссылке",
    "test_started": "Начал тест",
    "question_shown": "Показан вопрос",
    "answer_given": "Дал ответ",
    "test_completed": "Завершил тест",
    "access_granted_auto": "Доступ выдан (авто)",
    "access_denied": "Доступ не выдан",
    "access_granted_manual": "Доступ выдан (вручную)",
    "access_denied_manual": "Доступ отклонён (вручную)",
    "attempt_reset": "Попытка сброшена",
    "user_blocked": "Заблокирован",
    "admin_added": "Админ добавлен",
    "admin_removed": "Админ удалён",
    "resumed_session": "Продолжил тест",
    "setting_changed": "Настройка изменена",
}


async def cb_admin_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    parts = query.data.split(":")
    page = int(parts[1]) if len(parts) > 1 else 0
    per_page = 10

    logs, total = await db.get_logs_paginated(page * per_page, per_page)

    if not logs:
        text = "<blockquote><b>Логи</b>\n\nПусто.</blockquote>"
    else:
        lines = [f"<blockquote><b>Логи</b>  (стр. {page + 1}, всего {total})\n"]
        for log in logs:
            label = EVENT_LABELS.get(log["event_type"], log["event_type"])
            t = ts_short(log["created_at"])
            lines.append(f"<code>{t}</code>  {label}\n  user: <code>{log['user_id']}</code>")
        lines.append("</blockquote>")
        text = "\n".join(lines)

    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("< Назад", callback_data=f"al:{page - 1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton("Далее >", callback_data=f"al:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("Назад", callback_data="ap")])

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


async def cb_admin_user_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    parts = query.data.split(":")
    uid = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 0
    per_page = 10

    logs, total = await db.get_logs_paginated(page * per_page, per_page, user_id=uid)

    if not logs:
        text = f"<blockquote><b>Логи пользователя</b> <code>{uid}</code>\n\nПусто.</blockquote>"
    else:
        lines = [f"<blockquote><b>Логи пользователя</b> <code>{uid}</code>  ({total})\n"]
        for log in logs:
            label = EVENT_LABELS.get(log["event_type"], log["event_type"])
            t = ts_short(log["created_at"])
            payload = log.get("payload_json", "{}")
            lines.append(f"<code>{t}</code>  {label}")
        lines.append("</blockquote>")
        text = "\n".join(lines)

    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("<", callback_data=f"aul:{uid}:{page - 1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton(">", callback_data=f"aul:{uid}:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("Назад к карточке", callback_data=f"ad:{uid}")])

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


# Управление админами

async def cb_admin_list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await admin_check(query):
        return

    admins = await db.get_all_admins()
    lines = ["<blockquote><b>Админы</b>\n"]
    for a in admins:
        role_label = "SUPER" if a["role"] == "super_admin" else "admin"
        lines.append(f"{DOT} <code>{a['telegram_user_id']}</code>  [{role_label}]  добавлен {ts_to_str(a['added_at'])}")
    lines.append("</blockquote>")
    text = "\n".join(lines)

    is_super = await db.is_super_admin(query.from_user.id)
    buttons = []
    if is_super:
        buttons.append([InlineKeyboardButton("Добавить админа", callback_data="aaa")])
        buttons.append([InlineKeyboardButton("Удалить админа", callback_data="ada")])
    buttons.append([InlineKeyboardButton("Назад", callback_data="ap")])

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


async def cb_admin_add_admin_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await db.is_super_admin(query.from_user.id):
        await query.answer("Только super admin", show_alert=True)
        return
    context.user_data["awaiting_addadmin"] = True
    await query.edit_message_text(
        "<blockquote>Введите user_id нового админа:</blockquote>",
        parse_mode=ParseMode.HTML,
    )


async def cb_admin_del_admin_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await db.is_super_admin(query.from_user.id):
        await query.answer("Только super admin", show_alert=True)
        return
    context.user_data["awaiting_deladmin"] = True
    await query.edit_message_text(
        "<blockquote>Введите user_id админа для удаления:</blockquote>",
        parse_mode=ParseMode.HTML,
    )


# Настройки ссылок

async def cb_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await db.is_super_admin(query.from_user.id):
        await query.answer("Только super admin", show_alert=True)
        return

    ch, ct = await get_links()
    text = (
        f"<blockquote><b>Настройки ссылок</b>\n\n"
        f"{DOT} Канал:\n<code>{ch}</code>\n\n"
        f"{DOT} Чат:\n<code>{ct}</code></blockquote>"
    )
    buttons = [
        [InlineKeyboardButton("Изменить ссылку на канал", callback_data="aset_ch")],
        [InlineKeyboardButton("Изменить ссылку на чат", callback_data="aset_ct")],
        [InlineKeyboardButton("Назад", callback_data="ap")],
    ]
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


async def cb_admin_set_channel_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await db.is_super_admin(query.from_user.id):
        return
    context.user_data["awaiting_set_channel"] = True
    await query.edit_message_text(
        "<blockquote>Отправьте новую ссылку на канал:</blockquote>",
        parse_mode=ParseMode.HTML,
    )


async def cb_admin_set_chat_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not await db.is_super_admin(query.from_user.id):
        return
    context.user_data["awaiting_set_chat"] = True
    await query.edit_message_text(
        "<blockquote>Отправьте новую ссылку на чат:</blockquote>",
        parse_mode=ParseMode.HTML,
    )


# MAIN

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", cmd_start))

    # Callbackобработчики  тест
    app.add_handler(CallbackQueryHandler(cb_start_test, pattern=r"^st$"))
    app.add_handler(CallbackQueryHandler(cb_answer, pattern=r"^a:"))

    # Callback обработчики админка
    app.add_handler(CallbackQueryHandler(cb_admin_panel, pattern=r"^ap$"))
    app.add_handler(CallbackQueryHandler(cb_admin_stats, pattern=r"^as$"))
    app.add_handler(CallbackQueryHandler(cb_admin_sources, pattern=r"^asrc$"))
    app.add_handler(CallbackQueryHandler(cb_admin_users, pattern=r"^au:"))
    app.add_handler(CallbackQueryHandler(cb_admin_user_search_prompt, pattern=r"^aus$"))
    app.add_handler(CallbackQueryHandler(cb_admin_user_search_clear, pattern=r"^auc$"))
    app.add_handler(CallbackQueryHandler(cb_admin_user_detail, pattern=r"^ad:"))
    app.add_handler(CallbackQueryHandler(cb_admin_grant, pattern=r"^ag:"))
    app.add_handler(CallbackQueryHandler(cb_admin_deny, pattern=r"^an:"))
    app.add_handler(CallbackQueryHandler(cb_admin_reset, pattern=r"^ar:"))
    app.add_handler(CallbackQueryHandler(cb_admin_block, pattern=r"^ab:"))
    app.add_handler(CallbackQueryHandler(cb_admin_logs, pattern=r"^al:"))
    app.add_handler(CallbackQueryHandler(cb_admin_user_logs, pattern=r"^aul:"))
    app.add_handler(CallbackQueryHandler(cb_admin_list_admins, pattern=r"^ala$"))
    app.add_handler(CallbackQueryHandler(cb_admin_add_admin_prompt, pattern=r"^aaa$"))
    app.add_handler(CallbackQueryHandler(cb_admin_del_admin_prompt, pattern=r"^ada$"))
    app.add_handler(CallbackQueryHandler(cb_admin_settings, pattern=r"^aset$"))
    app.add_handler(CallbackQueryHandler(cb_admin_set_channel_prompt, pattern=r"^aset_ch$"))
    app.add_handler(CallbackQueryHandler(cb_admin_set_chat_prompt, pattern=r"^aset_ct$"))

    # Текстовые сообщения (для поиска / добавления админа)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Инициализация БД при старте
    import asyncio
    asyncio.new_event_loop().run_until_complete(db.init_db())

    logger.info("Bot started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
