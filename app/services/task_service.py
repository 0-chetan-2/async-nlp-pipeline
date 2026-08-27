from uuid import UUID

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