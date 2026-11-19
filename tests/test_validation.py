import pytest
from app.utils.document_validation import validate_text, validate_file_extension, validate_document_metadata

def test_validate_text_valid():
    assert validate_text("The court delivered its judgment.") == True

def test_validate_text_none():
    with pytest.raises(ValueError):
        validate_text(None)

def test_validate_text_blank():
    with pytest.raises(ValueError):
        validate_text("   ")

def test_validate_file_extension_valid():
    assert validate_file_extension("case.pdf") == True

def test_validate_file_extension_invalid():
    with pytest.raises(ValueError):
        validate_file_extension("case.exe")

def test_validate_document_metadata_valid():
    assert validate_document_metadata({"case_title": "ABC vs State", "court": "Supreme Court", "year": 2024}) == True

def test_validate_document_metadata_none():
    with pytest.raises(ValueError):
        validate_document_metadata(None)

def test_validate_document_metadata_missing_key():
    with pytest.raises(KeyError):
        validate_document_metadata({"case_title": "ABC vs State", "court": "Supreme Court"})

def test_validate_document_metadata_wrong_year_type():
    with pytest.raises(TypeError):
        validate_document_metadata({"case_title": "ABC vs State", "court": "Supreme Court", "year": "2024"})
