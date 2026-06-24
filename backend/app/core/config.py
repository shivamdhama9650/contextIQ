from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Enterprise Knowledge Assistant API"
    service_name: str = "enterprise-knowledge-assistant-api"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    backend_cors_origins: str = Field(
        default="http://localhost:3000",
        alias="BACKEND_CORS_ORIGINS",
    )
    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: str | None = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str | None = Field(
        default=None,
        alias="SUPABASE_SERVICE_ROLE_KEY",
    )
    embedding_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL_NAME",
    )
    embedding_batch_size: int = Field(default=96, alias="EMBEDDING_BATCH_SIZE")
    chunk_size: int = Field(default=1800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    processing_stale_minutes: int = Field(default=10, alias="PROCESSING_STALE_MINUTES")
    chroma_persist_dir: str = Field(default="./chroma_data", alias="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field(
        default="company_knowledge",
        alias="CHROMA_COLLECTION_NAME",
    )
    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    hf_token: str | None = Field(default=None, alias="HF_TOKEN")


    @property
    def cors_origins(self) -> list[str]:
        origins = [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

        # Browsers treat localhost and 127.0.0.1 as different origins.
        if self.app_env == "development":
            for origin in (
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ):
                if origin not in origins:
                    origins.append(origin)

        return origins

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
