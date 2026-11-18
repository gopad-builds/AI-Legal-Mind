from fastapi import APIRouter
from app.schemas.document import DocumentRequest,DocumentResponse
from app.services.document_service import process_document_metadata

router=APIRouter()


@router.post("/documents/metadata", response_model=DocumentResponse)
def submit_document_metadata(sample:DocumentRequest):
    result=process_document_metadata(sample)
    return result



