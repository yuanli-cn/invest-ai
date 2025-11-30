"""Trading days and calendar utilities."""

from datetime import date, timedelta
from typing import Any

try:
    import holidays

    _HOLIDAYS_AVAILABLE = True
except ImportError:
    # Fallback if holidays package is not available
    holidays = None  # type: ignore
    _HOLIDAYS_AVAILABLE = False


class TradingDaysChina:
    """Chinese trading days calendar."""

    def __init__(self) -> None:
        """Initialize the trading days calendar."""
        self.cn_holidays: Any = None  # holidays.CountryHoliday | None
        # Use Chinese holidays if available
        if _HOLIDAYS_AVAILABLE:
            self.cn_holidays = holidays.CountryHoliday("CN")
        else:
            # Simple fallback - just use weekends
            self.cn_holidays = None

    def is_trading_day(self, target_date: date) -> bool:
        """Check if a date is a trading day in China."""
        # Weekends are not trading days
        if target_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Check if it's a Chinese holiday
        if self.cn_holidays and target_date in self.cn_holidays:
            return False

        return True

    def get_previous_trading_day(
        self, target_date: date, max_days_back: int = 5
    ) -> date:
        """Get the previous trading day."""
        current_date = target_date - timedelta(days=1)

        for _ in range(max_days_back):
            if self.is_trading_day(current_date):
                return current_date
            current_date -= timedelta(days=1)

        # If no trading day found, return the last checked date
        return current_date

    def get_next_trading_day(
        self, target_date: date, max_days_forward: int = 5
    ) -> date:
        """Get the next trading day."""
        current_date = target_date + timedelta(days=1)

        for _ in range(max_days_forward):
            if self.is_trading_day(current_date):
                return current_date
            current_date += timedelta(days=1)

        # If no trading day found, return the last checked date
        return current_date

    def get_nearest_trading_day(
        self, target_date: date, prefer_backward: bool = True
    ) -> date:
        """Get the nearest trading day to the target date."""
        if self.is_trading_day(target_date):
            return target_date

        if prefer_backward:
            return self.get_previous_trading_day(target_date)
        else:
            return self.get_next_trading_day(target_date)

    def get_trading_dates_between(self, start_date: date, end_date: date) -> list[date]:
        """Get all trading dates between two dates (inclusive)."""
        trading_dates = []
        current_date = start_date

        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_dates.append(current_date)
            current_date += timedelta(days=1)

        return trading_dates

    def get_trading_days_in_year(self, year: int) -> list[date]:
        """Get all trading days in a specific year."""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        return self.get_trading_dates_between(start_date, end_date)

    def get_trading_days_in_month(self, year: int, month: int) -> list[date]:
        """Get all trading days in a specific month."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        return self.get_trading_dates_between(start_date, end_date)

    def count_trading_days_between(self, start_date: date, end_date: date) -> int:
        """Count trading days between two dates."""
        return len(self.get_trading_dates_between(start_date, end_date))

    def get_year_start_trading_day(self, year: int) -> date:
        """Get the first trading day of a year."""
        start_date = date(year, 1, 1)
        return self.get_next_trading_day(start_date)

    def get_year_end_trading_day(self, year: int) -> date:
        """Get the last trading day of a year."""
        end_date = date(year, 12, 31)
        return self.get_previous_trading_day(end_date)


# Global instance for reuse
_trading_days: TradingDaysChina | None = None


def get_trading_days() -> TradingDaysChina:
    """Get the global trading days instance."""
    global _trading_days
    if _trading_days is None:
        _trading_days = TradingDaysChina()
    return _trading_days


def is_trading_day(target_date: date) -> bool:
    """Check if a date is a trading day (convenience function)."""
    return get_trading_days().is_trading_day(target_date)


def get_nearest_trading_day(target_date: date, prefer_backward: bool = True) -> date:
    """Get the nearest trading day (convenience function)."""
    return get_trading_days().get_nearest_trading_day(target_date, prefer_backward)


def get_year_end_trading_day(year: int) -> date:
    """Get the last trading day of a year (convenience function)."""
    return get_trading_days().get_year_end_trading_day(year)


def get_year_start_trading_day(year: int) -> date:
    """Get the first trading day of a year (convenience function)."""
    return get_trading_days().get_year_start_trading_day(year)
