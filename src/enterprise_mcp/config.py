"""Application configuration loaded from environment variables."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings for the Enterprise Engineering Intelligence MCP."""

    app_name: str = "Enterprise Engineering Intelligence MCP"
    environment: str = "development"
    log_level: str = "INFO"

    groq_api_key: SecretStr | None = None
    groq_model: str = "openai/gpt-oss-120b"
    github_token: SecretStr | None = None
    github_api_base_url: str = "https://api.github.com"
    notion_token: SecretStr | None = None
    notion_api_base_url: str = "https://api.notion.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
