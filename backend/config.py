from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "AI Data Analyst"
    debug: bool = False

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # Storage paths
    upload_dir: str = "uploads"
    data_dir: str = "data"
    db_url: str = "sqlite:///./data/analyses.db"

    # Limits
    max_file_size_mb: int = 50
    max_rows_for_ml: int = 100_000
    max_cols_for_pairplot: int = 8
    top_categories_shown: int = 15

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
