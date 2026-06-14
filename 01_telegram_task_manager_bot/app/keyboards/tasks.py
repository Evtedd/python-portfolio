from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.task import Task, TaskStatus


def task_status_keyboard(task: Task) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text="New",
            callback_data=f"task_status:{task.id}:{TaskStatus.new.value}",
        ),
        InlineKeyboardButton(
            text="In progress",
            callback_data=f"task_status:{task.id}:{TaskStatus.in_progress.value}",
        ),
        InlineKeyboardButton(
            text="Done",
            callback_data=f"task_status:{task.id}:{TaskStatus.done.value}",
        ),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
