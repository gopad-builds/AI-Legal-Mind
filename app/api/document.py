from fastapi import APIRouter, HTTPException, UploadFile, File
from app.schemas.document import DocumentRequest, DocumentResponse
from app.schemas.ingestion import IngestionResponse
from app.services.document_service import process_document_metadata
from app.services.upload_service import safe_upload_file
from app.services.ingestion_service import process_document
import logging
from pathlib import Path
from app.parsers.pdf_parser import extract_pdf_document
from app.parsers.docx_parser import extract_docx_document
from app.core.config import settings

document_router = APIRouter()
logger = logging.getLogger(__name__)


@document_router.post("/documents/metadata", response_model=DocumentResponse)
def submit_document_metadata(request: DocumentRequest):
    logger.info("Received document metadata submission request.")
    return process_document_metadata(request)


@document_router.post("/documents/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    try:
        upload_result = await safe_upload_file(file)
        return process_document(upload_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await file.close()


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
