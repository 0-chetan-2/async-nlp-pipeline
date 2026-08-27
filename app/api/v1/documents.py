from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from app.core.database import get_db
from app.schemas.document import DocumentUploadResponse
from app.services.file_storage import save_file
from app.services.file_validator import validate_file
from app.services.task_service import create_task


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    await validate_file(file)

    content = await file.read()
    file_size = len(content)

    await file.seek(0)

    file_path = await save_file(file)

    try:
        task = await create_task(
                db=db,
                filename=file.filename,
                mime_type=file.content_type,
                file_size=file_size,
                file_path=file_path,
            )
    except Exception:
        Path(file_path).unlink(missing_ok=True)
        raise

    return DocumentUploadResponse(
        task_id=task.task_id
    )