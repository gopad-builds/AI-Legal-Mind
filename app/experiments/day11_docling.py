import time
from pathlib import Path
from docling.document_converter import DocumentConverter

FILE_PATH = "C:/Downloads/24596_2025_1_1501_67131_Judgement_19-Dec-2025.pdf"
MD_OUTPUT_PATH = "app/experiments/docling_output.md"


def run_docling_experiment():
    start_time = time.perf_counter()
    converter = DocumentConverter()
    result = converter.convert(FILE_PATH)
    elapsed = time.perf_counter() - start_time

    doc = result.document
    print(f"Conversion Status: {result.status}")
    print(f"Docling completed in {elapsed:.2f} seconds")

    # Step 3.2: Export Markdown
    markdown_text = doc.export_to_markdown()
    Path(MD_OUTPUT_PATH).write_text(markdown_text, encoding="utf-8")
    print(f"Saved Markdown to {MD_OUTPUT_PATH}")

    # Step 3.3: Inspect structured elements & Page Provenance (item.prov)
    print("/n--- SAMPLE STRUCTURED ITEMS & PROVENANCE ---")
    for item, level in list(doc.iterate_items())[:25]:
        page_no = item.prov[0].page_no if getattr(item, "prov", None) else "N/A"
        snippet = getattr(item, "text", "")[:70].replace("/n", " ")
        print(f"[Page {page_no}] Level={level} | Label={item.label} | Text={snippet}")

    # Step 3.4: Inspect Tables separately as DataFrames
    print(f"/n--- TABLES DETECTED: {len(doc.tables)} ---")
    for index, table in enumerate(doc.tables):
        df = table.export_to_dataframe(doc=doc)
        print(f"/nTable {index + 1}:")
        print(df.head(5))


if __name__ == "__main__":
    run_docling_experiment()
