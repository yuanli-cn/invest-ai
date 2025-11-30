"""Configuration settings management."""

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Basic settings
    app_name: str = "invest-ai"
    version: str = "0.1.0"
    debug: bool = Field(default=False, description="Debug mode")

    # Data settings
    default_data_dir: str = Field(default=".")
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)  # 1 hour

    # API settings
    tushare_token: str | None = Field(default=None)
    api_timeout: int = Field(default=30)
    api_retry_count: int = Field(default=3)
    api_retry_delay: float = Field(default=1.0)

    # Output settings
    default_format: str = Field(default="table")
    precision: int = Field(default=2)
    date_format: str = Field(default="%Y-%m-%d")

    # Trading settings
    default_currency: str = Field(default="CNY")
    trading_days_only: bool = Field(default=True)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings."""
        super().__init__(**kwargs)

    @property
    def tushare_configured(self) -> bool:
        """Check if Tushare API is properly configured."""
        return bool(self.tushare_token)

    @property
    def use_tushare(self) -> bool:
        """Check if we should use Tushare API."""
        return self.tushare_configured

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def load_settings() -> Settings:
    """Load application settings."""
    return Settings()


def get_env_file_path() -> str:
    """Get the path to the environment file."""
    return ".env"


def validate_settings(settings: Settings) -> list[str]:
    """Validate settings and return any issues."""
    issues = []

    # Check Tushare configuration
    if not settings.tushare_configured:
        issues.append(
            "Tushare token not configured. Set TUSHARE_TOKEN environment variable "
            "or add it to .env file. API calls for stock prices will fail."
        )

    # Check API timeout
    if settings.api_timeout <= 0:
        issues.append("API timeout must be positive")

    # Check retry settings
    if settings.api_retry_count < 0:
        issues.append("API retry count cannot be negative")
    if settings.api_retry_delay < 0:
        issues.append("API retry delay cannot be negative")

    # Check format
    if settings.default_format not in ["table", "json"]:
        issues.append("Default format must be 'table' or 'json'")

    # Check precision
    if settings.precision < 0 or settings.precision > 10:
        issues.append("Precision must be between 0 and 10")

    return issues


def print_configuration_warning(settings: Settings) -> None:
    """Print configuration warning if needed."""
    import sys

    issues = validate_settings(settings)
    if issues:
        print("Configuration warnings:", file=sys.stderr)
        for issue in issues:
            print(f"  ⚠️  {issue}", file=sys.stderr)
        print()
