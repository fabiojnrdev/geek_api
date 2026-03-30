# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configurações da aplicação.
    Carrega variáveis de ambiente do arquivo .env
    """
    
    # Aplicação
    app_name: str = "Geek Store API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./geek_store.db"
    
    # Security
    secret_key: str = "a8f5e2c9b1d4f7e3a6c8b2d5f9e1c4a7b3d6f8e2c5a9b1d4f7e3a6c8b2d5f9e1"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    """
    Retorna instância única das configurações (singleton).
    O decorator @lru_cache garante que seja criada apenas uma vez.
    """
    return Settings()


# Instância global para facilitar importação
settings = get_settings()