"""
Centralized configuration loaded from environment variables.

Keeping all tunables (model names, chunk sizes, paths) here means every
other module imports `settings` instead of reading os.environ directly,
which is the single-source-of-truth pattern the assignment's "System
Design" section asks for.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./storage/app.db"
    vector_store_dir: str = "./storage/vector_store"
    embedding_model: str = "all-MiniLM-L6-v2"
    knowledge_base_dir: str = "./app/knowledge_base"
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 4
    questions_per_session: int = 6

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# Roles the system currently supports. Each key must match a subfolder
# name under `knowledge_base_dir` and a collection name in the vector store.
SUPPORTED_ROLES = {
    "backend_engineer": "Backend Engineer",
    "ai_ml_engineer": "AI/ML Engineer",
    "data_scientist": "Data Scientist",
}
