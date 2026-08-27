from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskStatus


async def create_task(
    db: AsyncSession,
    filename: str,
    mime_type: str,
    file_size: int,
    file_path: str,
) -> Task:

    task = Task(
        status=TaskStatus.PENDING,
        filename=filename,
        mime_type=mime_type,
        file_size=file_size,
        file_path=file_path,
    )

    db.add(task)

    await db.commit()
    await db.refresh(task)

    return task


async def get_task(
    db: AsyncSession,
    task_id: UUID,
) -> Task | None:

    result = await db.execute(
        select(Task).where(Task.task_id == task_id)
    )

    return result.scalar_one_or_none()


async def update_task_status(
    db: AsyncSession,
    task_id: UUID,
    status: TaskStatus,
    error_code: str | None = None,
    error_message: str | None = None,
) -> Task | None:

    task = await get_task(db, task_id)

    if task is None:
        return None

    task.status = status
    task.error_code = error_code
    task.error_message = error_message

    await db.commit()
    await db.refresh(task)

    return task