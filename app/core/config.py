from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "survey-intelligence-service"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    database_url: str = Field(..., description="PostgreSQL DSN")

    embeddings_model_name: str = "BAAI/bge-m3"
    embeddings_dim: int = 1024
    embeddings_device: str = "cpu"
    embeddings_batch_size: int = 32
    embeddings_normalize: bool = True

    qwen_base_url: str = "http://qwen:8000"
    qwen_model_name: str = "qwen3"

    duplicate_exact_threshold: float = 0.97
    duplicate_semantic_threshold: float = 0.85


@lru_cache
def get_settings() -> Settings:
    return Settings()
