"""Application settings — loaded from environment / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://localhost/archon"

    # Clerk
    clerk_jwks_url: str = ""
    clerk_api_key: str = ""  # for reading user publicMetadata

    # Anthropic (passed through to archon library via env vars)
    anthropic_api_key: str = ""
    archon_model: str = "claude-haiku-4-5"
    archon_synthesis_model: str = "claude-sonnet-4-5"

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Dev
    debug: bool = False


settings = Settings()
