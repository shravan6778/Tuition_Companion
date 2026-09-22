from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    database_url: str
    supertokens_connection_uri: str = "http://localhost:3567"
    supertokens_api_key: str | None = None
    app_name: str = "Tuition Companion"
    api_domain: str = "http://localhost:8000"
    website_domain: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"


settings = Settings()