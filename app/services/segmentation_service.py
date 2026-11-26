import json
import logging
from pathlib import Path

from app.utils.segmentation_utils import (
    normalize_line,
    is_likely_heading,
    is_numbered_paragraph,
    extract_legal_references,
    extract_court_details,
)

logger = logging.getLogger(__name__)
STORAGE_PATH = Path("app/storage")


def _build_paragraph(text: str, paragraph_number: int | None, page_number: int) -> dict:
    return {
        "paragraph_number": paragraph_number,
        "text": text.strip(),
        "page_number": page_number,
        "legal_references": extract_legal_references(text),
    }


def segment_document(pages: list[dict]) -> dict:
    document_metadata = extract_court_details(pages)

    sections = []
    current_section = {"heading": "INTRODUCTION", "page_number": pages[0]["page_number"] if pages else 1, "content": []}

    for page in pages:
        page_number = page.get("page_number", 0)
        text = page.get("text", "")
        lines = text.split("\n")

        i = 0
        while i < len(lines):
            line = normalize_line(lines[i])

            if not line:
                i += 1
                continue

            if is_likely_heading(line):
                # Save current section if it has content
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"heading": line, "page_number": page_number, "content": []}
                i += 1
                continue

            is_numbered, para_num = is_numbered_paragraph(line)
            if is_numbered:
                # Collect continuation lines until next numbered para, heading or blank
                para_lines = [line]
                i += 1
                while i < len(lines):
                    next_line = normalize_line(lines[i])
                    if not next_line:
                        i += 1
                        break
                    if is_likely_heading(next_line):
                        break
                    next_is_numbered, _ = is_numbered_paragraph(next_line)
                    if next_is_numbered:
                        break
                    para_lines.append(next_line)
                    i += 1
                full_text = " ".join(para_lines)
                current_section["content"].append(
                    _build_paragraph(full_text, para_num, page_number)
                )
                continue

            # Unclassified text — never discard
            current_section["content"].append(
                _build_paragraph(line, None, page_number)
            )
            i += 1

    # Append last section
    if current_section["content"]:
        sections.append(current_section)

    return {
        "document_metadata": document_metadata,
        "sections": sections,
    }


def segment_and_save(document_id: str, pages: list[dict]) -> dict:
    result = segment_document(pages)
    output_path = STORAGE_PATH / f"{document_id}_segments.json"
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    logger.info("Segments saved for document %s", document_id)
    return result
