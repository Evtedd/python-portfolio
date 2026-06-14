import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.task import Task
from app.repositories.tasks import TaskRepository
from app.services.tasks import TaskService


@pytest.fixture()
async def task_service():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield TaskService(TaskRepository(session))

    await engine.dispose()
