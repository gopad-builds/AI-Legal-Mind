import logging
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from app.utils.document_validation import validate_file_extension

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
CHUNK_SIZE = 1024 * 1024

async def safe_upload_file(file: UploadFile) -> dict:
    original_filename = file.filename or ""

    validate_file_extension(original_filename)
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported content type: {file.content_type}")

    file_extension = Path(original_filename).suffix.lower()
    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}{file_extension}"

    upload_folder = Path(settings.upload_dir)
    upload_folder.mkdir(parents=True, exist_ok=True)
    file_path = upload_folder / safe_filename

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    total_bytes = 0

    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise ValueError(f"File size exceeds maximum limit of {settings.max_file_size_mb} MB.")
                f.write(chunk)

        if total_bytes == 0:
            raise ValueError("Uploaded file cannot be empty (0 bytes).")

    except Exception:
        if file_path.exists():
            file_path.unlink()
        raise

    logger.info(f"Saved '{original_filename}' as '{safe_filename}' ({total_bytes} bytes)")

    return {
        "document_id": document_id,
        "original_filename": original_filename,
        "stored_filename": safe_filename,
        "file_path": str(file_path),
        "file_size": total_bytes,
        "status": "UPLOADED",
    }
