from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Knowledge Assistant"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    database_url: str = ""

    default_top_k: int = 5
    default_max_context_chunks: int = 4
    default_chunk_size: int = 700
    default_chunk_overlap: int = 120

    embedding_provider: str = "local"
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    embedding_api_key: str = ""
    embedding_api_url: str = ""
    embedding_dim: int = 768
    
    llm_provider: str = "local"
    llm_model: str = "qwen3:14b"
    llm_api_key: str = ""
    llm_api_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
