from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import TaskStatusResponse
from app.services.result_service import get_result
from app.services.task_service import get_task

router = APIRouter()


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
)
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve task status and persisted result from PostgreSQL.
    """

    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID",
        )

    task = await get_task(
        db=db,
        task_id=task_uuid,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    result = None
    error = None

    if task.status.value == "SUCCESS":
        persisted_result = await get_result(
            db=db,
            task_id=task_uuid,
        )

        if persisted_result is not None:
            result = {
                "summary": persisted_result.summary,
                "chunk_count": persisted_result.chunk_count,
                "model_version": persisted_result.model_version,
            }

    elif task.status.value == "FAILED":
        error = task.error_message

    return TaskStatusResponse(
        task_id=str(task.task_id),
        status=task.status.value,
        result=result,
        error=error,
    )