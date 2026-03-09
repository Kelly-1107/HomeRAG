from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # Embedding
    embedding_provider: str = "openai"  # "openai" / "deepseek"
    openai_embedding_api_key: str = ""
    openai_embedding_base_url: str = "https://api.openai.com/v1"
    openai_embedding_model: str = "BAAI/bge-large-zh-v1.5"
    openai_embedding_dimensions: int = 1024

    # Database
    sqlite_url: str = "sqlite:///./homerag.db"
    chroma_persist_dir: str = "./chroma_data"

    # App
    default_user_id: str = "user_001"

    class Config:
        env_file = ".env"


settings = Settings()
