"""Market data specific models and utilities."""

from datetime import date, datetime

from invest_ai.models import InvestmentType, PriceData


class MarketDataCache:
    """Simple in-memory cache for market data."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize the cache with TTL in seconds."""
        self.cache: dict[str, tuple[PriceData, datetime]] = (
            {}
        )  # key -> (data, timestamp)
        self.ttl_seconds = ttl_seconds

    def _generate_key(self, code: str, date: date, source: str) -> str:
        """Generate cache key."""
        return f"{code}_{date}_{source}"

    def get(self, code: str, date: date, source: str) -> PriceData | None:
        """Get cached price data."""
        key = self._generate_key(code, date, source)
        if key in self.cache:
            data, timestamp = self.cache[key]
            from datetime import timedelta

            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                return data
            else:
                # Expired, remove from cache
                del self.cache[key]
        return None

    def set(self, code: str, date: date, source: str, data: PriceData) -> None:
        """Cache price data."""
        key = self._generate_key(code, date, source)
        from datetime import datetime

        self.cache[key] = (data, datetime.now())

    def clear(self) -> None:
        """Clear all cached data."""
        self.cache.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)


class PriceFetcherConfig:
    """Configuration for price fetching operations."""

    def __init__(
        self,
        max_concurrent_requests: int = 10,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        timeout_seconds: int = 30,
        validate_codes: bool = True,
    ):
        """Initialize the configuration."""
        self.max_concurrent_requests = max_concurrent_requests
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.timeout_seconds = timeout_seconds
        self.validate_codes = validate_codes


class MarketDataSummary:
    """Summary of market data for a set of investments."""

    def __init__(self) -> None:
        """Initialize the summary."""
        self.data_sources: dict[str, int] = {}
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        self.total_codes: int = 0
        self.missing_dates: int = 0

    def add_success(self, source: str) -> None:
        """Record a successful request."""
        self.successful_requests += 1
        self.data_sources[source] = self.data_sources.get(source, 0) + 1

    def add_failure(self) -> None:
        """Record a failed request."""
        self.failed_requests += 1

    def set_total_codes(self, count: int) -> None:
        """Set the expected total number of codes."""
        self.total_codes = count

    def add_missing_dates(self, count: int = 1) -> None:
        """Record missing date data."""
        self.missing_dates += count

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.successful_requests + self.failed_requests
        return (self.successful_requests / total) if total > 0 else 0.0

    @property
    def completeness(self) -> float:
        """Calculate data completeness."""
        return (
            (self.successful_requests / self.total_codes)
            if self.total_codes > 0
            else 0.0
        )


class InvestmentInfo:
    """Information about an investment (stock or fund)."""

    def __init__(
        self,
        code: str,
        name: str | None = None,
        investment_type: InvestmentType = InvestmentType.STOCK,
        is_valid: bool = True,
    ):
        """Initialize investment info."""
        self.code = code
        self.name = name
        self.investment_type = investment_type
        self.is_valid = is_valid
        self.market: str | None = None  # Shanghai/Shenzhen/etc.
        self.first_price_date: date | None = None
        self.last_price_date: date | None = None

    def __str__(self) -> str:
        """String representation."""
        return f"{self.code}{' - ' + self.name if self.name else ''} ({self.investment_type.value})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"InvestmentInfo(code='{self.code}', name='{self.name}', "
            f"type={self.investment_type.value}, valid={self.is_valid})"
        )


class PriceQuery:
    """A query for price data."""

    def __init__(
        self,
        codes: list[str],
        dates: list[date],
        investment_type: InvestmentType,
    ):
        """Initialize the query."""
        self.codes = codes
        self.dates = dates
        self.investment_type = investment_type
        self.sort_codes()
        self.sort_dates()

    def sort_codes(self) -> None:
        """Sort codes for consistent processing."""
        self.codes.sort()

    def sort_dates(self) -> None:
        """Sort dates for consistent processing."""
        self.dates.sort()

    @property
    def total_requests(self) -> int:
        """Total number of individual price requests."""
        return len(self.codes) * len(self.dates)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"PriceQuery({len(self.codes)} {self.investment_type.value}s, "
            f"{len(self.dates)} dates, {self.total_requests} requests)"
        )
