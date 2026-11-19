from fastapi import APIRouter
from app.schemas.document import DocumentRequest,DocumentResponse
from app.services.document_service import process_document_metadata
from app.core.logging_config import setup_logging
import logging
router=APIRouter()

logger = logging.getLogger(__name__)


@router.post("/documents/metadata", response_model=DocumentResponse)
def submit_document_metadata(request:DocumentRequest):
    logger.info("Received document metadata submission request.")
    result=process_document_metadata(request)
    return result



