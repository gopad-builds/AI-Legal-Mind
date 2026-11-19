from app.schemas.upload import UploadResponse
from app.services.upload_service import safe_upload_file
from fastapi import APIRouter, File, UploadFile, HTTPException
import logging

upload_router=APIRouter()

logger = logging.getLogger(__name__)

@upload_router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        result = await safe_upload_file(file)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error saving file.")

