"""Calculation-specific models and utilities."""

from datetime import date
from enum import Enum

from invest_ai.models import InvestmentType, PriceData


class CalculationStatus(str, Enum):
    """Status of calculation operations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MarketDataRequirement:
    """Defines market data requirements for calculations."""

    def __init__(self) -> None:
        """Initialize market data requirements."""
        self.required_dates: dict[str, list[date]] = {}
        self.current_prices_needed: set[str] = set()
        self.historical_prices_needed: set[str] = set()

    def add_year_end_price_requirement(self, code: str, year: int) -> None:
        """Add requirement for year-end price."""
        from ..market.trading_days import get_year_end_trading_day

        year_end_date = get_year_end_trading_day(year)

        if code not in self.required_dates:
            self.required_dates[code] = []
        self.required_dates[code].append(year_end_date)

    def add_year_start_price_requirement(self, code: str, year: int) -> None:
        """Add requirement for year-start price."""
        from ..market.trading_days import get_year_start_trading_day

        year_start_date = get_year_start_trading_day(year)

        if code not in self.required_dates:
            self.required_dates[code] = []
        self.required_dates[code].append(year_start_date)

    def add_current_price_requirement(self, code: str) -> None:
        """Add requirement for current price."""
        self.current_prices_needed.add(code)

    def get_unique_dates(self) -> set[date]:
        """Get all unique dates required."""
        unique_dates = set()
        for dates in self.required_dates.values():
            unique_dates.update(dates)
        return unique_dates

    def get_required_codes(self) -> set[str]:
        """Get all codes that require pricing."""
        codes = set(self.required_dates.keys())
        codes.update(self.current_prices_needed)
        return codes


class CalculationContext:
    """Context for a calculation operation."""

    def __init__(
        self,
        investment_type: InvestmentType,
        year: int | None = None,
        specific_code: str | None = None,
        calculation_type: str = "unknown",
    ):
        """Initialize calculation context."""
        self.investment_type = investment_type
        self.year = year
        self.specific_code = specific_code
        self.calculation_type = calculation_type  # "annual", "history", etc.
        self.status = CalculationStatus.PENDING
        self.created_at = date.today()
        self.completed_at: date | None = None
        self.error_message: str | None = None

    def mark_in_progress(self) -> None:
        """Mark calculation as in progress."""
        self.status = CalculationStatus.IN_PROGRESS

    def mark_completed(self) -> None:
        """Mark calculation as completed."""
        self.status = CalculationStatus.COMPLETED
        self.completed_at = date.today()

    def mark_failed(self, error_message: str) -> None:
        """Mark calculation as failed."""
        self.status = CalculationStatus.FAILED
        self.error_message = error_message
        self.completed_at = date.today()

    @property
    def is_complete(self) -> bool:
        """Check if calculation is complete."""
        return self.status in [CalculationStatus.COMPLETED, CalculationStatus.FAILED]

    @property
    def duration_days(self) -> int | None:
        """Get calculation duration in days."""
        if self.completed_at:
            return (self.completed_at - self.created_at).days
        return None


class PriceDataCache:
    """Simple caching for price data during calculations."""

    def __init__(self) -> None:
        """Initialize price cache."""
        self.cache: dict[str, dict[date, PriceData]] = {}

    def add_price_data(self, code: str, price_data: PriceData) -> None:
        """Add price data to cache."""
        if code not in self.cache:
            self.cache[code] = {}
        self.cache[code][price_data.price_date] = price_data

    def get_price_data(self, code: str, target_date: date) -> PriceData | None:
        """Get price data from cache."""
        return self.cache.get(code, {}).get(target_date)

    def get_latest_price_data(self, code: str) -> PriceData | None:
        """Get latest price data for a code."""
        if code not in self.cache or not self.cache[code]:
            return None
        return max(self.cache[code].items(), key=lambda x: x[0])[1]

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()

    def size(self) -> int:
        """Get cache size."""
        return sum(len(dates) for dates in self.cache.values())


class PerformanceMetrics:
    """Performance metrics for calculations."""

    def __init__(self) -> None:
        """Initialize performance metrics."""
        self.api_calls_made: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.calculation_time_ms: int = 0
        self.data_fetch_time_ms: int = 0
        self.start_time: float | None = None
        self.end_time: float | None = None

    def start_timing(self) -> None:
        """Start timing."""
        import time

        self.start_time = time.time()

    def end_timing(self) -> None:
        """End timing."""
        import time

        self.end_time = time.time()
        if self.start_time:
            self.calculation_time_ms = int((self.end_time - self.start_time) * 1000)

    @property
    def total_time_ms(self) -> int:
        """Get total time in milliseconds."""
        return self.calculation_time_ms + self.data_fetch_time_ms

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self.cache_hits + self.cache_misses
        return (self.cache_hits / total_requests) if total_requests > 0 else 0.0
