from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus


def get_task(
    db: Session,
    task_id: UUID,
) -> Task | None:

    return db.execute(
        select(Task).where(Task.task_id == task_id)
    ).scalar_one_or_none()


def update_task_status(
    db: Session,
    task_id: UUID,
    status: TaskStatus,
    error_code: str | None = None,
    error_message: str | None = None,
) -> Task | None:

    task = get_task(
        db=db,
        task_id=task_id,
    )

    if task is None:
        return None

    task.status = status
    task.error_code = error_code
    task.error_message = error_message

    return task