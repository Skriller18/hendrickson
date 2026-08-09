from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "hendrickson"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    vertex_project: str = ""
    vertex_location: str = "us-central1"
    ollama_base_url: str = "http://localhost:11434"

    default_llm_model: str = "gpt-5.6-terra"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    github_token: str = ""
    github_webhook_secret: str = ""

    jira_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""

    linear_api_key: str = ""

    backend_port: int = 8000
    backend_host: str = "0.0.0.0"
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
