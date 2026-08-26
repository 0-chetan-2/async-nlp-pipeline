from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    filename: str
    file_path: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


class NLPAnalysisResult(BaseModel):
    filename: str
    word_count: int
    char_count: int
    sentiment: Dict[str, float]
    keywords: list[str]
