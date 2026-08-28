from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models import Result
from app.workers.database import SessionLocal


MODEL_VERSION = "lexrank-v1"


def save_result(
    db: Session,
    task_id: UUID,
    summary: str,
    chunk_count: int,
) -> Result:

    existing_result = db.execute(
        select(Result).where(
            Result.task_id == task_id
        )
    ).scalar_one_or_none()

    if existing_result is not None:
        existing_result.summary = summary
        existing_result.chunk_count = chunk_count
        existing_result.model_version = MODEL_VERSION

        return existing_result

    result = Result(
        task_id=task_id,
        summary=summary,
        chunk_count=chunk_count,
        model_version=MODEL_VERSION,
    )

    db.add(result)

    return result


async def get_result(
    db: AsyncSession,
    task_id: UUID,
) -> Result | None:

    query_result = await db.execute(
        select(Result).where(
            Result.task_id == task_id
        )
    )

    return query_result.scalar_one_or_none()


def get_saved_result(
    task_id: UUID,
) -> Result | None:

    with SessionLocal() as db:
        return db.execute(
            select(Result).where(
                Result.task_id == task_id
            )
        ).scalar_one_or_none()