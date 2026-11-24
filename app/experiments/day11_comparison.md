# Day 11 Parser Comparison: PyMuPDF + Tesseract vs. Docling

**Test Document:** `complex_judgment.pdf` (15 pages — *K.P. Kirankumar @ Kiran v. State by Peenya Police*, 2025 INSC 1473)

## 1. Evaluation Matrix

| Evaluation Criteria | PyMuPDF + Tesseract | Docling | Notes / Observations |
| :--- | :--- | :--- | :--- |
| **Text extraction** | Good | Good | Both extract all body text accurately on born-digital pages. |
| **Heading identification** | Poor | Good | PyMuPDF outputs `FACTUAL BACKGROUND` as flat text; Docling tags it as `section_header`. |
| **Heading hierarchy** | Poor | Good | Docling preserves Markdown heading levels (`##`), whereas PyMuPDF has none. |
| **Reading order** | Partial | Good | PyMuPDF injects bottom-of-page footnotes (`3 P.W. 2 to...`) mid-sentence across page breaks. |
| **Table extraction** | Poor | Good | PyMuPDF shreds Page 3's 16-witness table across single-word lines; Docling preserves rows/columns. |
| **Page references** | Good | Good | PyMuPDF tracks `page_number` per page; Docling tracks `item.prov[0].page_no` per element. |
| **Bounding boxes** | Partial | Good | Available via `get_text("blocks")` in PyMuPDF, and natively via `item.prov[0].bbox` in Docling. |
| **Scanned PDF support** | Good | Good | PyMuPDF + Tesseract selectively OCRs scanned pages; Docling includes built-in OCR. |
| **Processing time** | Good (~0.05s) | Poor (~XX.XXs warm) | PyMuPDF is near-instant on CPU; Docling runs deep-learning layout/table models. |
| **Ease of integration** | Good | Partial | PyMuPDF is lightweight; Docling adds heavy PyTorch/vision model dependencies. |

## 2. Specific Experiments Summary
* **Experiment A (Headings):** Headings like `FACTUAL BACKGROUND`, `FINDINGS RECORDED BY THE COURTS BELOW:`, and `ANALYSIS:` appear as plain strings in `pymupdf_output.txt`, while Docling labels them as `section_header` and formats them with Markdown `#` prefixes.
* **Experiment B (Table Extraction — Page 3 Witness Table):** PyMuPDF splits cell text across dozens of lines, breaking the link between `S.No.`, `Particulars`, and `Description`. Docling reconstructs a clean Markdown table and DataFrame preserving all 16 rows.
* **Experiment C & D (Reading Order & Provenance):** In PyMuPDF, Page 3's Paragraph 5 is interrupted by Footnote 3 (`3 P.W. 2 to P.W. 6...`). In Docling, `item.prov[0].page_no` maps every paragraph and table back to its exact page number without breaking sentence flow.
* **Experiment E (Processing Time):** PyMuPDF finished in ~`[insert your seconds]`s, while Docling finished in `[insert your seconds]`s (warm run on CPU).

## 3. Architecture Decision (Task 5)
* **Selected Approach:** **Option C — Hybrid Approach**
* **Why It Fits LegalMind AI:** Indian legal judgments range from simple single-column orders to complex judgments containing witness tables, compensation schedules, and dense footnotes. Using **PyMuPDF + Tesseract** as the fast default path keeps CPU cost and latency low for simple documents, while routing table-heavy or complex layout PDFs to **Docling** preserves structural integrity and accurate citations for RAG.
* **Remaining Limitations & Scale Plan:** Docling is CPU-heavy (~1–2s/page). When document volume increases, parsing should run asynchronously via background workers (Days 41–42) with OCR disabled on born-digital pages (`do_ocr=False`) to cut Docling runtime roughly in half.
