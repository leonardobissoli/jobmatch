from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the local-only Job Match runtime."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    log_level: str = Field(default="INFO")
    minimax_api_key: str = Field(default="")
    minimax_base_url: str = Field(default="https://api.minimax.io/v1")
    minimax_model: str = Field(default="MiniMax-M2.7")
    minimax_timeout_seconds: int = Field(default=180)

    local_llm_enabled: bool = Field(default=True)
    local_llm_timeout_seconds: int = Field(default=300)
    # Docker uses host.docker.internal to reach Ollama/LM Studio on the host.
    # Native development keeps localhost. This value is server-controlled and
    # never accepted from an HTTP request.
    local_llm_host: str = Field(default="localhost")

    cors_allowed_origins: str = Field(default="http://localhost:3000")
    max_cv_bytes: int = Field(default=5 * 1024 * 1024)
    max_job_bytes: int = Field(default=100 * 1024)

    @property
    def cors_origins_list(self) -> list[str]:
        return [value.strip() for value in self.cors_allowed_origins.split(",") if value.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
