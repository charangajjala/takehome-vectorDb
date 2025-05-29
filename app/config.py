from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = False
    )

    APP_HOST: str     = Field("0.0.0.0", description="API bind host")
    APP_PORT: int     = Field(8000,    description="API bind port")
    DEBUG: bool       = Field(False,   description="Enable debug mode")

    REPO_TYPE: str    = Field("inmemory", description="inmemory | future DB types")
    INDEXER_TYPE: str = Field("vptree",    description="bruteforce | vptree ")

    COHERE_API_KEY: Optional[str] = Field(
        None,
        description="(Optional) Cohere API key for embedding-driven tests"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
