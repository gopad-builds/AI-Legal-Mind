from fastapi.testclient import TestClient
from app.main import app
import io
from app.core.config import settings
from pathlib import Path

client = TestClient(app)

def test_upload_valid_pdf():
    file_content = b"%PDF-1.4 valid pdf content"
    response = client.post(
        "/upload",
        files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200

def test_upload_invalid_extension():
    response = client.post(
        "/upload",
        files={"file": ("malware.exe", io.BytesIO(b"some content"), "application/pdf")}
    )
    assert response.status_code == 400

def test_upload_invalid_content_type():
    response = client.post(
        "/upload",
        files={"file": ("test.pdf", io.BytesIO(b"some content"), "text/plain")}
    )
    assert response.status_code == 400

def test_upload_empty_file():
    response = client.post(
        "/upload",
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
    )
    assert response.status_code == 400

def test_upload_file_too_large():
    large_content = b"a" * (11 * 1024 * 1024)  # 11MB, exceeds 10MB limit
    response = client.post(
        "/upload",
        files={"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")}
    )
    assert response.status_code == 400

def test_upload_valid_docx():
    file_content = b"PK valid docx content"
    response = client.post(
        "/upload",
        files={"file": ("test.docx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200

def test_path_traversal_filename():
    file_content = b"%PDF-1.4 valid pdf content"
    response = client.post(
        "/upload",
        files={"file": ("../../malicious.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "/" not in data["file_name"]
    assert "\\" not in data["file_name"]
    saved_path = Path(settings.upload_dir) / data["file_name"]
    assert saved_path.exists()

def test_file_saved_to_disk():
    file_content = b"%PDF-1.4 valid pdf content"
    response = client.post(
        "/upload",
        files={"file": ("saved_check.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    saved_path = Path(settings.upload_dir) / data["file_name"]
    assert saved_path.exists()

def test_response_schema():
    file_content = b"%PDF-1.4 valid pdf content"
    response = client.post(
        "/upload",
        files={"file": ("schema_check.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "file_name" in data
    assert "status" in data
    assert "message" in data

    file_content = b"%PDF-1.4 valid pdf content"
    response = client.post(
        "/upload",
        files={"file": ("schema_check.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "filename" in data
    assert "status" in data
    assert "message" in data