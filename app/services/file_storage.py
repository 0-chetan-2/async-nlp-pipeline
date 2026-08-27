from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


UPLOAD_DIR = Path("uploads")


async def save_file(file: UploadFile) -> str:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename).suffix.lower()

    stored_filename = f"{uuid4()}{extension}"

    file_path = UPLOAD_DIR / stored_filename

    content = await file.read()

    file_path.write_bytes(content)

    return str(file_path)