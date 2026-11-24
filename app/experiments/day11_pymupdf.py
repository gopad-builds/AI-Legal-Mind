import time
from pathlib import Path
from app.parsers.pdf_parser import extract_pdf_document

FILE_PATH = "C:/Downloads/24596_2025_1_1501_67131_Judgement_19-Dec-2025.pdf"
OUTPUT_PATH = "app/experiments/pymupdf_output.txt"


def run_pymupdf_baseline():
    start_time = time.perf_counter()
    result = extract_pdf_document(FILE_PATH)
    elapsed = time.perf_counter() - start_time

    lines = []
    for page in result["content"]:
        header = f"/n--- PAGE {page['page_number']} (scanned={page['is_scanned']}) ---/n"
        lines.append(header)
        lines.append(page["text"])

    full_text = "".join(lines)
    Path(OUTPUT_PATH).write_text(full_text, encoding="utf-8")

    print(f"PyMuPDF completed in {elapsed:.2f} seconds")
    print(f"Saved output to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_pymupdf_baseline()
