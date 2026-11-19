from fastapi import FastAPI
from app.utils.text_utils import clean_text,count_words
from app.utils.document_utils import sample_document,inspect_document,get_unique_sections,get_total_word_count,get_case_date
from app.api.document import document_router
from app.api.upload import upload_router 
from app.core.config import Settings
from app.core.logging_config import setup_logging
import logging




settings = Settings()
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

app.include_router(document_router)
app.include_router(upload_router)

logger.info("LegalMindAI started successfully")

@app.get("/health")
def health():
    logger.info("Health check endpoint called.")
    return {
    "application": "LegalMind AI",
    "status": "running"
}

@app.get("/text-test")
def text_test(text):
    cleaned_text=clean_text(text)
    words_count=count_words(cleaned_text)
    return {"original text":text,
            "Cleaned text": cleaned_text,
            "Word count": words_count}

@app.get("/document-test")
def document_text():
    inspection=inspect_document(sample_document)
    unique_sections=get_unique_sections(sample_document)
    total_word_count=get_total_word_count(sample_document)
    case_date=get_case_date(sample_document)
    return {"Document Inspection": inspection,
            "Unique Sections": unique_sections,
            "Total Word Count": total_word_count,
            "Case Date": case_date}


