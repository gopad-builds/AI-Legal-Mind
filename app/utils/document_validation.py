from pathlib import Path


def validate_text(text):
    if not text:
        raise ValueError("Input text cannot be empty")
    if not text.strip():
        raise ValueError("Input text cannot contain only blank spaces")
    return True


def validate_file_extension(filename):
    file_extension=Path(filename).suffix.lower()
    if file_extension not in ['.pdf', '.docx']:
        raise ValueError(f"Unsupported file type: {file_extension}")
    return True

def validate_document_metadata(metadata):
    if metadata is None:
        raise ValueError("Metadata cannot be None")
    if type(metadata) != dict:
        raise TypeError("Metadata must be a dictionary")
    for key in ['case_title', 'court', 'year']:
        if key not in metadata:
            raise KeyError(f"Metadata must contain '{key}'")
    if not metadata['case_title'] or not metadata['court']:
        raise ValueError("Metadata must contain 'case_title' and 'court'")
    if type(metadata['year']) != int:
        raise TypeError("Year must be an integer")
    return True

if __name__ == "__main__":
    validate_text("The court delivered its judgment.")
    # validate_text("  ")
    validate_file_extension("judgement.pdf")
    validate_file_extension("case.exe")
    
