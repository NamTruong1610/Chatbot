# app/config/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
  
    # ADMIN_API_KEY: str

    # ── OpenAI ───────────────────────────────────────────
    OPENAI_API_KEY: str

    # ── Qdrant (Vector DB) ───────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "business_domains"

    # ── Redis (Session Store) ────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_TTL_SECONDS: int = 3600             # 1 hour

    # ── PostgreSQL (Persistent Store) ────────────────────
    POSTGRES_URL: str

    # ── App ──────────────────────────────────────────────
    APP_ENV: str = "development"                # "development" | "production"
    ALLOWED_ORIGINS: list[str] = ["*"]          # lock down in production

    # ── File Upload ──────────────────────────────────────
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt", ".json", ".html"]

    # ── Chunking ─────────────────────────────────────────
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 50

    # ── LLM ──────────────────────────────────────────────
    LLM_MODEL: str = "gpt-4o"
    LLM_MAX_TOKENS: int = 1000
    LLM_TEMPERATURE: float = 0.7

    # ── Embedding ────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_TOP_K: int = 5                    # how many chunks to retrieve

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Single instance imported everywhere
settings = Settings()