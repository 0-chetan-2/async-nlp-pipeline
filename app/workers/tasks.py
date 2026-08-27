import os
from uuid import UUID

from app.models import TaskStatus
from app.services.nlp.service import NLPService
from app.workers import celery_app
from app.workers.task_service import update_task_status
from app.services.result_service import save_result


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

    Phase 5:
    - PENDING → PROCESSING
    - Extract document text
    - Clean text
    - Chunk text
    - Generate summary
    - Calculate NLP statistics
    - PROCESSING → SUCCESS
    - Record failures as FAILED
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

        # Run NLP pipeline
        result = NLPService.process_document(
            file_path
        )

        print(
            f"NLP processing completed for task "
            f"{task_id}"
        )

        print(f"Chunk count: {result['chunk_count']}")
        print(f"Word count: {result['word_count']}")
        print(f"Sentence count: {result['sentence_count']}")

        # Persist NLP result
        save_result(
            task_id=task_uuid,
            summary=result["summary"],
            chunk_count=result["chunk_count"],
        )

        # PROCESSING → SUCCESS
        update_task_status(
            task_id=task_uuid,
            status=TaskStatus.SUCCESS,
        )

        return {
            "task_id": task_id,
            **result,
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