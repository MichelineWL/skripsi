import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Document Continuity Assistant"
    app_env: str = "development"
    debug: bool = True

    # Gemini
    gemini_api_key: str = ""
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_http_client: str = "httpx"

    # Qdrant
    qdrant_path: str = "storage/qdrant"
    qdrant_collection_name: str = "dca_chunks"
    qdrant_vector_size: int = 3072

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

# Configure Gemini SDK transport before creating its client.
os.environ.setdefault(
    "GOOGLE_GENAI_HTTP_CLIENT",
    settings.gemini_http_client,
)