from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str = "Agentic QA Planning Assistant"
    DEBUG: bool = False

    PUBLIC_BASE_URL: str = "http://localhost:8000"

    CORS_ORIGINS: str = "http://localhost:3000"

    DATABASE_URL: str

    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Comma-separated in env, list here. Credentialed requests can't use "*"."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()