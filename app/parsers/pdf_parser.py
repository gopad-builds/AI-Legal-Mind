import pymupdf
import pytesseract
from PIL import Image
from pathlib import Path
import io
import logging

logger = logging.getLogger(__name__)
SCANNED_TEXT_THRESHOLD = 20

def _ocr_page(page) -> tuple[str, str]:
    try:
        pixmap = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pixmap.tobytes("png")))
        text = pytesseract.image_to_string(img)
        return text, "tesseract"
    except Exception as e:
        logger.error(f"OCR failed on page {page.number + 1}: {e}")
        return "", "ocr_failed"

def _extract_page(page, page_number: int) -> dict:
    text = page.get_text()
    is_scanned = len(text.strip()) < SCANNED_TEXT_THRESHOLD

    if is_scanned:
        text, extraction_method = _ocr_page(page)
    else:
        extraction_method = "pymupdf"

    return {
        "unit_type": "page",
        "paragraph_number": None,
        "page_number": page_number,
        "text": text,
        "is_scanned": is_scanned,
        "extraction_method": extraction_method
    }

def extract_pdf_document(file_path: str) -> dict:
    doc = pymupdf.open(file_path)
    try:
        metadata = doc.metadata
        return {
            "metadata": {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "page_count": doc.page_count,
                "file_name": Path(file_path).name,
                "file_type": "pdf"
            },
            "content": [
                _extract_page(doc.load_page(i), i + 1)
                for i in range(doc.page_count)
            ]
        }
    finally:
        doc.close()
