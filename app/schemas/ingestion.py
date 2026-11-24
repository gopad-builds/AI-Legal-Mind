from pydantic import BaseModel, Field
from typing import List, Optional

class IngestionError(BaseModel):
    error_code: str
    message: str

class IngestionResponse(BaseModel):
    document_id: str
    original_filename: str
    file_type: str
    file_hash: Optional[str] = None
    status: str
    total_units: int
    extracted_units: int
    warnings: List[str] = Field(default_factory=list)
    errors: List[IngestionError] = Field(default_factory=list)
    duplicate_of: Optional[str] = None
