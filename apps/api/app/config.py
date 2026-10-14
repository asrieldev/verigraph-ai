from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    demo_mode: bool = True
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    database_url: str = "postgresql+psycopg://verigraph:verigraph@localhost:5432/verigraph"
    redis_url: str = "redis://localhost:6379/0"
    allowed_github_hosts: str = "github.com"
    max_repository_mb: int = 50
    max_file_bytes: int = 500_000
    sandbox_timeout_seconds: int = 120
    data_dir: Path = Path("data")


settings = Settings()
