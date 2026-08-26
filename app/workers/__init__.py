import os
import time
from celery import Celery
from app.core.config import settings
from app.services import NLPService

celery_app = Celery(
    "async_nlp_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="process_nlp_document", bind=True)
def process_nlp_document(self, file_path: str, original_filename: str):
    """
    Celery task to asynchronously process uploaded document text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")

    # Read document content
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Simulate heavy processing delay if text is small
    time.sleep(1)

    # Perform NLP analysis using NLPService
    analysis_results = NLPService.extract_text_stats(content)
    analysis_results["filename"] = original_filename

    return analysis_results
