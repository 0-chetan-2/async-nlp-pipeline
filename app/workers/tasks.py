from app.workers import celery_app


@celery_app.task(name="test_celery_task")
def test_celery_task(message: str):
    print(f"Worker received: {message}")

    return {
        "message": message,
        "status": "processed",
    }