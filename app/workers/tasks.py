import os
from uuid import UUID

from app.models import TaskStatus
from app.workers import celery_app
from app.workers.task_service import update_task_status


@celery_app.task(
    name="process_document_task",
    bind=True,
)
def process_document_task(
    self,
    task_id: str,
    file_path: str,
):
    """
    Process an uploaded document asynchronously.

    Phase 4:
    - PENDING → PROCESSING
    - Verify file exists
    - PROCESSING → SUCCESS
    - Record failures as FAILED

    Actual NLP processing comes in Phase 5.
    """

    task_uuid = UUID(task_id)

    try:

        # PENDING → PROCESSING
        update_task_status(
            task_id=task_uuid,
            status=TaskStatus.PROCESSING,
        )

        print(f"Processing task: {task_id}")
        print(f"File path: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        file_size = os.path.getsize(file_path)

        print(
            f"Task {task_id}: "
            f"file exists, size={file_size} bytes"
        )

        # PROCESSING → SUCCESS
        update_task_status(
            task_id=task_uuid,
            status=TaskStatus.SUCCESS,
        )

        return {
            "task_id": task_id,
            "status": "processed",
            "file_size": file_size,
        }

    except Exception as exc:

        # PROCESSING → FAILED
        update_task_status(
            task_id=task_uuid,
            status=TaskStatus.FAILED,
            error_code=type(exc).__name__,
            error_message=str(exc),
        )

        raise