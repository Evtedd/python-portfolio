import csv
from io import StringIO

from app.models.task import Task, TaskStatus
from app.repositories.tasks import TaskRepository
from app.services.parser import parse_task_message


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    async def add_from_message(self, owner_id: int, message_text: str) -> Task:
        parsed = parse_task_message(message_text)
        return await self.repository.create(
            owner_id=owner_id,
            text=parsed.text,
            deadline_at=parsed.deadline_at,
            category=parsed.category,
        )

    async def change_status(
        self,
        owner_id: int,
        task_id: int,
        status: TaskStatus,
    ) -> Task:
        task = await self.repository.update_status(owner_id, task_id, status)
        if task is None:
            raise LookupError("Task was not found")
        return task

    async def export_csv(self, owner_id: int) -> bytes:
        tasks = await self.repository.list_for_user(owner_id=owner_id, limit=5000)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "text",
                "category",
                "status",
                "deadline_at",
                "created_at",
                "done_at",
            ],
        )
        for task in tasks:
            writer.writerow(
                [
                    task.id,
                    task.text,
                    task.category or "",
                    task.status,
                    task.deadline_at.isoformat() if task.deadline_at else "",
                    task.created_at.isoformat() if task.created_at else "",
                    task.done_at.isoformat() if task.done_at else "",
                ],
            )
        return output.getvalue().encode("utf-8")
