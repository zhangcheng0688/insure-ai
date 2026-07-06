"""Application configuration management."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from environment variables / .env file."""

    # LLM
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    anthropic_api_key: str = ""

    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"

    # Database
    database_url: str = "sqlite:///./insure_ai.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Storage
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"

    # App
    app_name: str = "InsureAI"
    app_version: str = "0.1.0"
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_llm_config(self, provider: Optional[str] = None) -> dict:
        """Return LiteLLM-compatible config dict for a provider."""
        p = provider or self.default_llm_provider
        configs = {
            "openai": {
                "api_key": self.openai_api_key,
                "api_base": self.openai_base_url,
            },
            "deepseek": {
                "api_key": self.deepseek_api_key,
                "api_base": self.deepseek_base_url,
            },
            "qwen": {
                "api_key": self.qwen_api_key,
                "api_base": self.qwen_base_url,
            },
            "anthropic": {
                "api_key": self.anthropic_api_key,
            },
        }
        return configs.get(p, configs["openai"])


settings = Settings()

# Ensure directories exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
