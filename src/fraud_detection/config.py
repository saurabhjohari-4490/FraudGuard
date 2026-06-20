"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "info"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://fraud:fraud_secret@localhost:5432/fraud_detection"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20

    # Scoring
    enrichment_timeout_ms: int = 50
    scoring_timeout_ms: int = 100

    # Mock Data Generator
    mock_tps: int = 10
    mock_fraud_rate: float = 0.05
    mock_seed: int = 42
    mock_enabled: bool = False  # Auto-start mock generator on boot

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
