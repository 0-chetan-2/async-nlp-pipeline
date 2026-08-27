from uuid import UUID

from sqlalchemy import select

from app.models import Task, TaskStatus
from app.workers.database import SessionLocal


def update_task_status(
    task_id: UUID,
    status: TaskStatus,
    error_code: str | None = None,
    error_message: str | None = None,
) -> Task | None:

    with SessionLocal() as db:

        task = db.execute(
            select(Task).where(Task.task_id == task_id)
        ).scalar_one_or_none()

        if task is None:
            return None

        task.status = status
        task.error_code = error_code
        task.error_message = error_message

        db.commit()
        db.refresh(task)

        return task