from uuid import UUID

from sqlalchemy import select

from app.models import Result
from app.workers.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


MODEL_VERSION = "lexrank-v1"


def save_result(
    task_id: UUID,
    summary: str,
    chunk_count: int,
) -> Result:
    """
    Persist the NLP result for a task.

    The task_id is the primary key of the results table,
    so each task can have only one result.
    """

    with SessionLocal() as db:

        existing_result = db.execute(
            select(Result).where(Result.task_id == task_id)
        ).scalar_one_or_none()

        if existing_result is not None:
            existing_result.summary = summary
            existing_result.chunk_count = chunk_count
            existing_result.model_version = MODEL_VERSION

            db.commit()
            db.refresh(existing_result)

            return existing_result

        result = Result(
            task_id=task_id,
            summary=summary,
            chunk_count=chunk_count,
            model_version=MODEL_VERSION,
        )

        db.add(result)

        db.commit()
        db.refresh(result)

        return result
    
async def get_result(
    db: AsyncSession,
    task_id: UUID,
) -> Result | None:

    query_result = await db.execute(
        select(Result).where(Result.task_id == task_id)
    )

    return query_result.scalar_one_or_none()