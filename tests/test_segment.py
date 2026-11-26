from app.utils.segmentation_utils import (
    is_likely_heading,
    is_numbered_paragraph,
    extract_legal_references,
    extract_court_details,
)
from app.services.segmentation_service import segment_document


# Test 1 — known uppercase heading detected
def test_known_heading():
    assert is_likely_heading("JUDGMENT") is True
    assert is_likely_heading("FACTUAL BACKGROUND") is True
    assert is_likely_heading("CONCLUSION") is True


# Test 2 — numbered paragraph detected, number extracted correctly
def test_numbered_paragraph():
    is_num, num = is_numbered_paragraph("3. The prosecution case is that...")
    assert is_num is True
    assert num == 3

    is_num, num = is_numbered_paragraph("(2) The appellant contended that...")
    assert is_num is True
    assert num == 2


# Test 3 — legal references extracted from paragraph
def test_legal_references():
    text = "The appellant was charged under Section 302 IPC and Article 21 of the Constitution."
    refs = extract_legal_references(text)
    assert any("302" in r for r in refs)
    assert any("21" in r for r in refs)


# Test 4 — court name NOT treated as heading
def test_court_name_not_heading():
    assert is_likely_heading("IN THE SUPREME COURT OF INDIA") is False
    assert is_likely_heading("IN THE HIGH COURT OF DELHI") is False


# Test 5 — unclassified text is not lost
def test_unclassified_text_preserved():
    pages = [
        {
            "page_number": 1,
            "text": "JUDGMENT\n\n1. Leave granted.\n\nSome unclassified remark here."
        }
    ]
    result = segment_document(pages)
    all_texts = [
        unit["text"]
        for section in result["sections"]
        for unit in section["content"]
    ]
    assert any("unclassified remark" in t for t in all_texts)


# Test 6 — court details extracted from first page
def test_court_details_extracted():
    pages = [
        {
            "page_number": 1,
            "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPEAL NO. 123/2025\nJOYMALYA BAGCHI, J.\nJUDGMENT\n1. Leave granted."
        }
    ]
    result = segment_document(pages)
    assert "SUPREME COURT" in result["document_metadata"]["court"]
    assert "123" in result["document_metadata"]["case_number"]
