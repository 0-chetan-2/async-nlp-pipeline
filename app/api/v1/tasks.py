from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult
from app.schemas import TaskStatusResponse
from app.workers import celery_app

router = APIRouter()


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Retrieve status and result of an async NLP task by ID.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None,
        "error": None
    }

    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)

    return response
