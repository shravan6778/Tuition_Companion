from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    database_url: str = "postgresql+psycopg://postgres:Postgresql21@localhost:5432/tuition"
    firebase_credentials_path: str = "./firebase-service-account.json"
    cors_origins: str = "http://localhost:5173"


settings = Settings()