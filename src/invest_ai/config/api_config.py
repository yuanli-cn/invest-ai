"""API configuration classes."""

from pydantic import BaseModel, Field


class TushareConfig(BaseModel):
    """Tushare API configuration."""

    base_url: str = Field(
        default="https://api.tushare.pro", description="Tushare API base URL"
    )
    token: str | None = Field(default=None, description="Tushare API token")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries")
    retry_delay: float = Field(
        default=1.0, description="Delay between retries in seconds"
    )
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    daily_limit: int = Field(
        default=200, description="Daily API call limit (free tier)"
    )

    @property
    def is_configured(self) -> bool:
        """Check if Tushare is properly configured."""
        return bool(self.token)


class EastMoneyConfig(BaseModel):
    """East Money API configuration."""

    base_url: str = Field(
        default="http://api.fund.eastmoney.com", description="East Money API base URL"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries")
    retry_delay: float = Field(
        default=1.0, description="Delay between retries in seconds"
    )
    referer: str = Field(
        default="http://fund.eastmoney.com", description="Referer header for requests"
    )
    user_agent: str = Field(
        default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        description="User-Agent header",
    )

    @property
    def is_configured(self) -> bool:
        """Check if East Money is properly configured."""
        return True  # East Money doesn't require authentication


class APIConfig(BaseModel):
    """Combined API configuration."""

    tushare: TushareConfig = Field(default_factory=TushareConfig)
    eastmoney: EastMoneyConfig = Field(default_factory=EastMoneyConfig)

    @property
    def stock_client_available(self) -> bool:
        """Check if stock price client is available."""
        return self.tushare.is_configured

    @property
    def fund_client_available(self) -> bool:
        """Check if fund NAV client is available."""
        return self.eastmoney.is_configured

    def get_headers(self, provider: str) -> dict[str, str]:
        """Get appropriate headers for API provider."""
        if provider == "eastmoney":
            return {
                "User-Agent": self.eastmoney.user_agent,
                "Referer": self.eastmoney.referer,
                "Accept": "application/json",
            }
        elif provider == "tushare":
            return {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        return {}

    def validate_config(self) -> list[str]:
        """Validate API configuration and return issues."""
        issues = []

        if not self.tushare.is_configured:
            issues.append(
                "Tushare API token not configured - stock prices will be unavailable"
            )

        if not self.eastmoney.is_configured:
            issues.append(
                "East Money API not properly configured - fund data will be unavailable"
            )

        if self.tushare.timeout <= 0:
            issues.append("Tushare timeout must be positive")

        if self.eastmoney.timeout <= 0:
            issues.append("East Money timeout must be positive")

        return issues


def create_api_config() -> APIConfig:
    """Create API configuration from settings."""
    from .settings import load_settings

    settings = load_settings()

    tushare_config = TushareConfig(
        token=settings.tushare_token,
    )

    eastmoney_config = EastMoneyConfig()

    return APIConfig(
        tushare=tushare_config,
        eastmoney=eastmoney_config,
    )
