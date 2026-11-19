from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_submit_document_metadata_valid():
    response = client.post("/documents/metadata", json={
        "case_title": "ABC vs State",
        "court": "Supreme Court of India",
        "year": 2024,
        "document_type": "judgment"
    })
    assert response.status_code == 200

def test_submit_document_metadata_invalid():
    response = client.post("/documents/metadata", json={
        "court": "Supreme Court of India",
        "year": 2024
    })
    assert response.status_code == 422
