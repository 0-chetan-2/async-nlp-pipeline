from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "async_nlp_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)