import pymupdf
from pathlib import Path

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
                {
                    "unit_type": "page",
                    "paragraph_number": None,
                    "page_number": i + 1,
                    "text": doc.load_page(i).get_text()
                }
                for i in range(doc.page_count)
            ]
        }
    finally:
        doc.close()
