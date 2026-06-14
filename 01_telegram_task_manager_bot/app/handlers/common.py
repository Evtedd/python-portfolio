from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.db.session import SessionFactory
from app.keyboards.tasks import task_status_keyboard
from app.models.task import Task, TaskStatus
from app.repositories.tasks import TaskRepository
from app.services.tasks import TaskService

router = Router()


def render_task(task: Task) -> str:
    deadline = (
        f"\nDeadline: {task.deadline_at:%d.%m.%Y %H:%M}"
        if task.deadline_at
        else ""
    )
    category = f"\nCategory: {task.category}" if task.category else ""
    return f"#{task.id} [{task.status}] {task.text}{category}{deadline}"


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Task bot is ready.\n"
        "Use /add text with a due marker and category, /list, /search text, "
        "/stats or /export.",
    )


@router.message(Command("add"))
async def add_task(message: Message) -> None:
    payload = message.text.removeprefix("/add").strip() if message.text else ""
    if not payload:
        await message.answer("Send task text after /add.")
        return

    async with SessionFactory() as session:
        service = TaskService(TaskRepository(session))
        try:
            task = await service.add_from_message(message.from_user.id, payload)
        except ValueError as exc:
            await message.answer(str(exc))
            return

    await message.answer(render_task(task), reply_markup=task_status_keyboard(task))


@router.message(Command("list"))
async def list_tasks(message: Message) -> None:
    args = message.text.removeprefix("/list").strip().split() if message.text else []
    status = None
    category = None
    for arg in args:
        try:
            status = TaskStatus(arg)
            continue
        except ValueError:
            pass

        if arg.startswith("#"):
            category = arg[1:]

    async with SessionFactory() as session:
        tasks = await TaskRepository(session).list_for_user(
            owner_id=message.from_user.id,
            status=status,
            category=category,
        )

    if not tasks:
        await message.answer("No tasks found.")
        return

    await message.answer("\n\n".join(render_task(task) for task in tasks))


@router.message(Command("search"))
async def search_tasks(message: Message) -> None:
    query = message.text.removeprefix("/search").strip() if message.text else ""
    if not query:
        await message.answer("Send search text after /search.")
        return

    async with SessionFactory() as session:
        tasks = await TaskRepository(session).list_for_user(
            owner_id=message.from_user.id,
            query=query,
        )

    if not tasks:
        await message.answer("Nothing found.")
        return

    await message.answer("\n\n".join(render_task(task) for task in tasks))


@router.message(Command("stats"))
async def stats(message: Message) -> None:
    async with SessionFactory() as session:
        data = await TaskRepository(session).weekly_stats(message.from_user.id)

    await message.answer(
        "Week stats:\n"
        f"Created: {data['created']}\n"
        f"Done: {data['done']}\n"
        f"Overdue: {data['overdue']}",
    )


@router.message(Command("export"))
async def export_tasks(message: Message) -> None:
    async with SessionFactory() as session:
        service = TaskService(TaskRepository(session))
        content = await service.export_csv(message.from_user.id)

    await message.answer_document(
        BufferedInputFile(content, filename="tasks.csv"),
        caption="Your tasks export.",
    )


@router.callback_query(lambda call: call.data and call.data.startswith("task_status:"))
async def update_task_status(call: CallbackQuery) -> None:
    _, task_id, status = call.data.split(":")
    async with SessionFactory() as session:
        service = TaskService(TaskRepository(session))
        try:
            task = await service.change_status(
                owner_id=call.from_user.id,
                task_id=int(task_id),
                status=TaskStatus(status),
            )
        except LookupError:
            await call.answer("Task was not found.", show_alert=True)
            return

    await call.message.edit_text(render_task(task), reply_markup=task_status_keyboard(task))
    await call.answer("Status updated.")
