"""
cerberus</> Configuration Management using Pydantic Settings.
Supports loading from environment variables and .env files.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Security Settings
    SECRET_KEY: str = "cerberus_dev_secret_key_change_in_production_32chars"
    API_KEY_PREFIX: str = "cvai_"
    RATE_LIMIT_PER_HOUR: int = 100
    DEFAULT_DEV_API_KEY: str = "cvai_dev_key_123"

    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./cerberus.db"

    # Cache Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 604800  # 7 days

    # LLM Provider Configuration
    LLM_PROVIDER: str = "heuristic"  # Options: watsonx, openai, ollama, heuristic
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "codellama"

    # Active Agents
    ENABLED_AGENTS: str = "security,performance,quality,architecture,compliance"

    # Review Tuning
    SEVERITY_THRESHOLD: str = "medium"
    BLOCKING_MODE: bool = False
    PROMETHEUS_ENABLED: bool = True

    @property
    def enabled_agents_list(self) -> List[str]:
        return [a.strip().lower() for a in self.ENABLED_AGENTS.split(",") if a.strip()]


# Global singleton settings instance
settings = Settings()
