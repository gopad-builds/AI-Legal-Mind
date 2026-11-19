from pydantic import BaseModel, Field
from typing import Optional

class UploadResponse(BaseModel):
    document_id: int
    file_name: str
    message: str
    status: str