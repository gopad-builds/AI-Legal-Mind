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
CHUNK_SIZE = 1024 * 1024  # 1 MB per chunk


async def safe_upload_file(file: UploadFile) -> dict:
    original_filename = file.filename or ""

    # 1. Validate Extension & Content-Type before touching file bytes
    validate_file_extension(original_filename)
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported content type: {file.content_type}")

    # 2. Generate safe filename & target path
    file_extension = Path(original_filename).suffix.lower()
    safe_filename = f"{uuid.uuid4().hex}{file_extension}"

    upload_folder = Path(settings.upload_dir)
    upload_folder.mkdir(parents=True, exist_ok=True)
    file_path = upload_folder / safe_filename

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    total_bytes = 0

    # 3. Stream file in 1 MB chunks directly to disk
    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                total_bytes += len(chunk)

                # Stop immediately as soon as limit is exceeded
                if total_bytes > max_bytes:
                    raise ValueError(
                        f"File size exceeds maximum limit of {settings.max_file_size_mb} MB."
                    )

                f.write(chunk)

        # Reject 0-byte empty files after loop finishes
        if total_bytes == 0:
            raise ValueError("Uploaded file cannot be empty (0 bytes).")

    except Exception:
        # Clean up partial or empty file if validation failed mid-stream
        if file_path.exists():
            file_path.unlink()
        raise

    logger.info(
        f"Saved '{original_filename}' safely as '{safe_filename}' ({total_bytes} bytes)"
    )

    return {
        "document_id":  uuid.uuid4().int >> 96,
        "file_name": safe_filename,
        "status": "UPLOADED",
        "message": f"File '{original_filename}' uploaded and saved successfully.",
    }
