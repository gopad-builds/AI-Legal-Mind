from pydantic import BaseModel,Field
from typing import Optional

class DocumentRequest(BaseModel):
    # Required AND non-empty (at least 1 character)
    document_type: str = Field(..., min_length=1)
    court: str = Field(..., min_length=1)
    
    # Required AND positive integer (strictly greater than 0)
    year: int = Field(..., gt=0)    
    # Optional (defaults to None), but if provided, must be non-empty
    case_title: Optional[str] = Field(default=None, min_length=1)


class DocumentResponse(BaseModel):
    document_id: int
    message:str
    case_title: str
    status:str