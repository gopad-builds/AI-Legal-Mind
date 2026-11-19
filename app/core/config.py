from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_version: str
    debug: bool
    database_url: str
    secret_key: SecretStr

    # Required so Pydantic reads D:\LegalMindAI\.env
    model_config = SettingsConfigDict(env_file=".env")


