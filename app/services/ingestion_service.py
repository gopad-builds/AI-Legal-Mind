import hashlib
import json
import logging
import tempfile
from pathlib import Path

from app.parsers.pdf_parser import extract_pdf_document
from app.parsers.docx_parser import extract_docx_document
from app.schemas.ingestion import IngestionError, IngestionResponse
from app.utils.text_utils import clean_document

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("app/storage/metadata_registry.json")
STORAGE_PATH = Path("app/storage")


def _calculate_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _read_registry() -> dict:
    if not REGISTRY_PATH.exists() or REGISTRY_PATH.stat().st_size == 0:
        return {"documents": []}
    try:
        with open(REGISTRY_PATH, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        logger.error("metadata_registry.json is malformed — manual recovery required")
        raise RuntimeError("Metadata registry is corrupted. Manual recovery required.")

    # Issue 4: validate registry structure
    if not isinstance(data, dict) or "documents" not in data or not isinstance(data["documents"], list):
        logger.error("metadata_registry.json has invalid structure")
        raise RuntimeError("Metadata registry has invalid structure. Manual recovery required.")

    return data


def _write_registry(registry: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Issue 2: unique temp file to avoid collision
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=REGISTRY_PATH.parent,
            suffix=".tmp",
            delete=False
        ) as f:
            json.dump(registry, f, indent=2)
            tmp_path = Path(f.name)
        tmp_path.replace(REGISTRY_PATH)
    except Exception:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()
        raise


def _check_duplicate(file_hash: str, registry: dict) -> str | None:
    for doc in registry["documents"]:
        if (
            doc["file_hash"] == file_hash
            and doc["status"] in {"PROCESSED", "PARTIALLY_PROCESSED"}
        ):
            return doc["document_id"]
    return None


def _attach_provenance(content: list, document_id: str, original_filename: str, file_type: str, file_hash: str) -> tuple[list, list]:
    enriched = []
    warnings = []
    for unit in content:
        if unit.get("extraction_method") == "ocr_failed":
            warnings.append(f"OCR failed on page {unit.get('page_number')}")
        enriched.append({
            "document_id": document_id,
            "original_filename": original_filename,
            "file_type": file_type,
            "file_hash": file_hash,
            **unit
        })
    return enriched, warnings


def _quality_check(content: list) -> tuple[str, list[IngestionError]]:
    total = len(content)
    if total == 0:
        return "FAILED", [IngestionError(error_code="EMPTY_EXTRACTION", message="No content units extracted")]

    failed_ocr = [u for u in content if u.get("extraction_method") == "ocr_failed"]
    usable = [u for u in content if u.get("text", "").strip()]

    if len(usable) == 0:
        return "FAILED", [IngestionError(error_code="EMPTY_EXTRACTION", message="All extracted units are empty")]

    if failed_ocr:
        return "PARTIALLY_PROCESSED", []

    return "PROCESSED", []


def _save_content(document_id: str, document_id_val: str, original_filename: str, file_type: str, file_hash: str, parsed_metadata: dict, enriched_content: list) -> None:
    # Issue 1: save parser metadata alongside enriched content
    # Issue 3: ensure storage directory exists
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    content_path = STORAGE_PATH / f"{document_id}_content.json"
    document_data = {
        "document_id": document_id_val,
        "original_filename": original_filename,
        "file_type": file_type,
        "file_hash": file_hash,
        "metadata": parsed_metadata,
        "content": enriched_content
    }
    with open(content_path, "w") as f:
        json.dump(document_data, f, indent=2)


def _register_document(registry: dict, document_id: str, original_filename: str, stored_filename: str, file_hash: str, file_type: str, status: str) -> None:
    registry["documents"].append({
        "document_id": document_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_hash": file_hash,
        "file_type": file_type,
        "status": status
    })
    _write_registry(registry)


def process_document(upload_result: dict) -> IngestionResponse:
    document_id = upload_result["document_id"]
    original_filename = upload_result["original_filename"]
    stored_filename = upload_result["stored_filename"]
    file_path = upload_result["file_path"]
    file_extension = Path(original_filename).suffix.lower()
    file_type = file_extension.lstrip(".")

    file_hash = _calculate_hash(file_path)
    registry = _read_registry()
    existing_id = _check_duplicate(file_hash, registry)

    if existing_id:
        Path(file_path).unlink(missing_ok=True)
        logger.info("Duplicate detected: %s matches existing document %s", original_filename, existing_id)
        return IngestionResponse(
            document_id=existing_id,
            original_filename=original_filename,
            file_type=file_type,
            file_hash=file_hash,
            status="DUPLICATE",
            total_units=0,
            extracted_units=0,
            duplicate_of=existing_id
        )

    if file_extension not in {".pdf", ".docx"}:
        Path(file_path).unlink(missing_ok=True)
        return IngestionResponse(
            document_id=document_id,
            original_filename=original_filename,
            file_type=file_type,
            status="FAILED",
            total_units=0,
            extracted_units=0,
            errors=[IngestionError(error_code="UNSUPPORTED_FORMAT", message=f"Unsupported file type: {file_extension}")]
        )

    try:
        if file_extension == ".pdf":
            parsed = extract_pdf_document(file_path)
        else:
            parsed = extract_docx_document(file_path)
    except Exception:
        logger.exception("Parser error for document %s", document_id)
        _register_document(registry, document_id, original_filename, stored_filename, file_hash, file_type, "FAILED")
        return IngestionResponse(
            document_id=document_id,
            original_filename=original_filename,
            file_type=file_type,
            file_hash=file_hash,
            status="FAILED",
            total_units=0,
            extracted_units=0,
            errors=[IngestionError(error_code="PARSER_ERROR", message="Unable to parse document")]
        )

    content = parsed.get("content", [])
    parsed_metadata = parsed.get("metadata", {})
    # Clean extracted text before quality check and provenance
    content = clean_document(content)
    total_units = len(content)
    status, errors = _quality_check(content)

    enriched_content, warnings = _attach_provenance(content, document_id, original_filename, file_type, file_hash)
    extracted_units = sum(1 for u in enriched_content if u.get("text", "").strip())

    # Issue 1 + 3: save complete document data with metadata, ensure dir exists
    _save_content(document_id, document_id, original_filename, file_type, file_hash, parsed_metadata, enriched_content)

    _register_document(registry, document_id, original_filename, stored_filename, file_hash, file_type, status)

    return IngestionResponse(
        document_id=document_id,
        original_filename=original_filename,
        file_type=file_type,
        file_hash=file_hash,
        status=status,
        total_units=total_units,
        extracted_units=extracted_units,
        warnings=warnings,
        errors=errors
    )
