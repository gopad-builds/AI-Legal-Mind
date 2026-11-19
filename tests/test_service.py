from app.schemas.document import DocumentRequest
from app.services.document_service import process_document_metadata

def test_process_document_metadata():
    request = DocumentRequest(case_title="ABC vs State", court="Supreme Court", year=2024, document_type="judgment")
    result = process_document_metadata(request)
    assert result["document_id"] == 101
    assert result["case_title"] == "ABC vs State"
    assert result["status"] == "accepted"
    assert "message" in result
