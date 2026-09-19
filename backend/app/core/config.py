from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    database_url: str
    firebase_credentials_path: str = "./firebase-service-account.json"
    cors_origins: str = "http://localhost:5173"


settings = Settings()