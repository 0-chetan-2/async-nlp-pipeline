import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status
from app.core.config import settings
from app.schemas import DocumentResponse, TaskResponse
from app.workers import process_nlp_document

router = APIRouter()


@router.post("/upload", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document file to trigger an asynchronous NLP pipeline processing task.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{file_ext}"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Trigger async Celery task
    task = process_nlp_document.delay(file_path, file.filename)

    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message="Document uploaded and queued for async NLP processing."
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents():
    """
    List uploaded documents and metadata.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    files = os.listdir(settings.UPLOAD_DIR)
    docs = []
    for f in files:
        if f != ".gitkeep":
            docs.append(DocumentResponse(
                filename=f,
                file_path=os.path.join(settings.UPLOAD_DIR, f),
                status="STORED"
            ))
    return docs
