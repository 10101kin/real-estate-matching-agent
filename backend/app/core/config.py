from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Real Estate Event Registration API"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "sqlite:///./app.db"
    blob_storage_path: str = "./blob_storage"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def ensure_paths(self) -> None:
        Path(self.blob_storage_path).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_paths()
