from pydantic import BaseModel

class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    message: str
    status: str
