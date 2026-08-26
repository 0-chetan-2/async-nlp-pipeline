from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Async NLP Pipeline"
    app_version: str = "1.0.0"

    database_url: str
    redis_url: str

    api_key: str

    upload_dir: str = "uploads"
    max_file_size: int = 50 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()