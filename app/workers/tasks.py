import os
from uuid import UUID

from celery.exceptions import SoftTimeLimitExceeded

from app.models import TaskStatus
from app.services.error_classifier import classify_error
from app.services.nlp.service import NLPService
from app.services.result_service import (
    get_saved_result,
    save_result,
)
from app.workers import celery_app
from app.workers.database import SessionLocal
from app.workers.task_service import update_task_status


@celery_app.task(
    name="process_document_task",
    bind=True,
    max_retries=3,
    soft_time_limit=60,
    time_limit=90,
)
def process_document_task(
    self,
    task_id: str,
    file_path: str,
):
    """
    Process an uploaded document asynchronously.

    Lifecycle:
        PENDING → PROCESSING → SUCCESS
                            ↘ FAILED

    Retryable errors:
        ConnectionError
        TimeoutError

    Permanent errors:
        All other exceptions.

    Time limits:
        Soft limit: 60 seconds
        Hard limit: 90 seconds
    """

    task_uuid = UUID(task_id)

    try:
        # --------------------------------------------------
        # Retry-safe check
        # --------------------------------------------------
        existing_result = get_saved_result(task_uuid)

        if existing_result is not None:
            print(
                f"Existing result found for task {task_id}. "
                "Skipping NLP processing."
            )

            with SessionLocal.begin() as db:
                update_task_status(
                    db=db,
                    task_id=task_uuid,
                    status=TaskStatus.SUCCESS,
                )

            return {
                "task_id": task_id,
                "summary": existing_result.summary,
                "chunk_count": existing_result.chunk_count,
                "model_version": existing_result.model_version,
            }

        # --------------------------------------------------
        # PENDING → PROCESSING
        # --------------------------------------------------
        with SessionLocal.begin() as db:
            update_task_status(
                db=db,
                task_id=task_uuid,
                status=TaskStatus.PROCESSING,
            )

        print(f"Processing task: {task_id}")
        print(f"File path: {file_path}")

        # --------------------------------------------------
        # Validate file exists
        # --------------------------------------------------
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        # --------------------------------------------------
        # NLP processing
        # --------------------------------------------------
        result = NLPService.process_document(
            file_path
        )

        print(
            f"NLP processing completed for task {task_id}"
        )

        print(
            f"Chunk count: {result['chunk_count']}"
        )
        print(
            f"Word count: {result['word_count']}"
        )
        print(
            f"Sentence count: {result['sentence_count']}"
        )

        # --------------------------------------------------
        # Result + SUCCESS in one transaction
        # --------------------------------------------------
        with SessionLocal.begin() as db:

            save_result(
                db=db,
                task_id=task_uuid,
                summary=result["summary"],
                chunk_count=result["chunk_count"],
            )

            update_task_status(
                db=db,
                task_id=task_uuid,
                status=TaskStatus.SUCCESS,
            )

        return {
            "task_id": task_id,
            **result,
        }

    # ------------------------------------------------------
    # Retryable errors
    # ------------------------------------------------------
    except (ConnectionError, TimeoutError) as exc:

        retries = self.request.retries

        if retries < self.max_retries:
            print(
                f"Retryable error for task {task_id}: {exc}"
            )

            print(
                f"Retry {retries + 1}/{self.max_retries}"
            )

            raise self.retry(
                exc=exc,
                countdown=2 ** retries,
            )

        error_code = classify_error(exc)

        with SessionLocal.begin() as db:
            update_task_status(
                db=db,
                task_id=task_uuid,
                status=TaskStatus.FAILED,
                error_code=error_code.value,
                error_message=f"Retries exhausted: {exc}",
            )

        raise

    # ------------------------------------------------------
    # Processing timeout
    # ------------------------------------------------------
    except SoftTimeLimitExceeded:

        with SessionLocal.begin() as db:
            update_task_status(
                db=db,
                task_id=task_uuid,
                status=TaskStatus.FAILED,
                error_code="PROCESSING_TIMEOUT",
                error_message=(
                    "Document processing exceeded "
                    "the 60 second limit."
                ),
            )

        raise

    # ------------------------------------------------------
    # Permanent failure
    # ------------------------------------------------------
    except Exception as exc:

        error_code = classify_error(exc)

        with SessionLocal.begin() as db:
            update_task_status(
                db=db,
                task_id=task_uuid,
                status=TaskStatus.FAILED,
                error_code=error_code.value,
                error_message=str(exc),
            )

        raise