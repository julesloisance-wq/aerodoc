"""Runtime settings, read from environment variables or a local `.env` file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://aerodoc:aerodoc@localhost:5432/aerodoc"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    seed: int = 42


@lru_cache
def get_settings() -> Settings:
    return Settings()
