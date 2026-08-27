import os

from app.workers import celery_app


@celery_app.task(name="process_document_task")
def process_document_task(
    task_id: str,
    file_path: str,
):
    """
    Phase 4:
    Verify that the uploaded document can be processed asynchronously.

    Actual NLP processing will be added in Phase 5.
    """

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

    return {
        "task_id": task_id,
        "status": "processed",
        "file_size": file_size,
    }