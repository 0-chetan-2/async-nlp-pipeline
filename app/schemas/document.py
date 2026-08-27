from uuid import UUID

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    task_id: UUID