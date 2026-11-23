from docx import Document
from pathlib import Path

def extract_docx_document(file_path: str) -> dict:
    document = Document(file_path)
    props = document.core_properties
    content = []
    paragraph_number = 1

    for paragraph in document.paragraphs:
        if not paragraph.text.strip():
            continue
        content.append({
            "unit_type": "paragraph",
            "paragraph_number": paragraph_number,
            "page_number": None,
            "text": paragraph.text.strip()
        })
        paragraph_number += 1

    return {
        "metadata": {
            "title": props.title or "",
            "author": props.author or "",
            "page_count": None,
            "file_name": Path(file_path).name,
            "file_type": "docx"
        },
        "content": content
    }
