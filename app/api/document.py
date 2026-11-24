from fastapi import APIRouter, HTTPException
from app.schemas.document import DocumentRequest,DocumentResponse
from app.services.document_service import process_document_metadata
import logging
from pathlib import Path
from app.parsers.pdf_parser import extract_pdf_document
from app.parsers.docx_parser import extract_docx_document
from app.core.config import settings
document_router=APIRouter()

logger = logging.getLogger(__name__)


@document_router.post("/documents/metadata", response_model=DocumentResponse)
def submit_document_metadata(request:DocumentRequest):
    logger.info("Received document metadata submission request.")
    result=process_document_metadata(request)
    return result


@document_router.get("/documents/pdf-test")
def pdf_test():
    upload_folder = Path(settings.upload_dir)
    pdf_files = list(upload_folder.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="No PDF found in storage folder.")
    return extract_pdf_document(str(pdf_files[0]))


@document_router.get("/documents/docx-test")
def docx_test():
    upload_folder = Path(settings.upload_dir)
    docx_files = list(upload_folder.glob("*.docx"))
    if not docx_files:
        raise HTTPException(status_code=404, detail="No DOCX found in storage folder.")    
    return extract_docx_document(str(docx_files[0]))