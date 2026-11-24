from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



class Settings(BaseSettings):
    app_name: str
    app_version: str
    debug: bool
    database_url: str
    secret_key: SecretStr
    upload_dir: str
    max_file_size_mb: int

    # Required so Pydantic reads D:\LegalMindAI\.env
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()


