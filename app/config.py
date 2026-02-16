from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Geek Store API"
    app_version: str = "1.0.0"
    debug: bool = False

    #Database
    database_url: str = "sqlite:///./test.db"

    #Segurança
    secret_key: str ="a8fd9e8c7b6a5f4r3e2d1c0b9a8f9e7d6c85f4a3b2c1d0e9f8g7h6i5j4k3l2m1n0o9p8q7r6s5t4u3v2w1x0y9z8"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    #CORS
    allowed_origins: list[str] = ["*"]
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @lru_cache()
    def get_settings() -> "Settings":
        return Settings()
    Settings = get_settings()