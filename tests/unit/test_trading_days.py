"""Tests for trading days module."""

import pytest
from datetime import date

from invest_ai.market.trading_days import (
    TradingDaysChina,
    get_trading_days,
    is_trading_day,
    get_nearest_trading_day,
    get_year_end_trading_day,
    get_year_start_trading_day,
)


class TestTradingDaysChina:
    """Tests for TradingDaysChina class."""

    def test_init(self):
        """Test initialization."""
        tdc = TradingDaysChina()
        assert tdc is not None

    def test_is_trading_day_weekday(self):
        """Test is_trading_day for weekday."""
        tdc = TradingDaysChina()
        # 2023-01-03 is Tuesday
        assert tdc.is_trading_day(date(2023, 1, 3)) is True

    def test_is_trading_day_weekend(self):
        """Test is_trading_day for weekend."""
        tdc = TradingDaysChina()
        # 2023-01-07 is Saturday
        assert tdc.is_trading_day(date(2023, 1, 7)) is False
        # 2023-01-08 is Sunday
        assert tdc.is_trading_day(date(2023, 1, 8)) is False

    def test_get_previous_trading_day(self):
        """Test get_previous_trading_day."""
        tdc = TradingDaysChina()
        # From Monday, previous should be Friday
        monday = date(2023, 1, 9)  # Monday
        prev = tdc.get_previous_trading_day(monday)
        assert prev.weekday() == 4  # Friday

    def test_get_previous_trading_day_from_weekend(self):
        """Test get_previous_trading_day from weekend."""
        tdc = TradingDaysChina()
        saturday = date(2023, 1, 7)
        prev = tdc.get_previous_trading_day(saturday)
        assert prev.weekday() == 4  # Friday

    def test_get_next_trading_day(self):
        """Test get_next_trading_day."""
        tdc = TradingDaysChina()
        # From Friday, next should be Monday
        friday = date(2023, 1, 6)  # Friday
        next_day = tdc.get_next_trading_day(friday)
        assert next_day.weekday() == 0  # Monday

    def test_get_next_trading_day_from_weekend(self):
        """Test get_next_trading_day from weekend."""
        tdc = TradingDaysChina()
        saturday = date(2023, 1, 7)
        next_day = tdc.get_next_trading_day(saturday)
        assert next_day.weekday() == 0  # Monday

    def test_get_nearest_trading_day_already_trading(self):
        """Test get_nearest_trading_day when already a trading day."""
        tdc = TradingDaysChina()
        tuesday = date(2023, 1, 3)
        result = tdc.get_nearest_trading_day(tuesday)
        assert result == tuesday

    def test_get_nearest_trading_day_backward(self):
        """Test get_nearest_trading_day preferring backward."""
        tdc = TradingDaysChina()
        saturday = date(2023, 1, 7)
        result = tdc.get_nearest_trading_day(saturday, prefer_backward=True)
        assert result.weekday() == 4  # Friday

    def test_get_nearest_trading_day_forward(self):
        """Test get_nearest_trading_day preferring forward."""
        tdc = TradingDaysChina()
        saturday = date(2023, 1, 7)
        result = tdc.get_nearest_trading_day(saturday, prefer_backward=False)
        assert result.weekday() == 0  # Monday

    def test_get_trading_dates_between(self):
        """Test get_trading_dates_between."""
        tdc = TradingDaysChina()
        # A week's worth
        start = date(2023, 1, 2)  # Monday
        end = date(2023, 1, 8)  # Sunday
        result = tdc.get_trading_dates_between(start, end)
        # Should have 5 weekdays
        assert len(result) == 5

    def test_get_trading_days_in_year(self):
        """Test get_trading_days_in_year."""
        tdc = TradingDaysChina()
        days = tdc.get_trading_days_in_year(2023)
        # Should have roughly 250-260 trading days (excluding holidays)
        assert len(days) > 200
        assert len(days) <= 262  # Max weekdays in a year

    def test_get_trading_days_in_month(self):
        """Test get_trading_days_in_month."""
        tdc = TradingDaysChina()
        days = tdc.get_trading_days_in_month(2023, 1)
        # January typically has 20-23 trading days
        assert len(days) >= 18
        assert len(days) <= 23

    def test_get_trading_days_in_december(self):
        """Test get_trading_days_in_month for December."""
        tdc = TradingDaysChina()
        days = tdc.get_trading_days_in_month(2023, 12)
        assert len(days) >= 18
        assert len(days) <= 23

    def test_count_trading_days_between(self):
        """Test count_trading_days_between."""
        tdc = TradingDaysChina()
        start = date(2023, 1, 2)
        end = date(2023, 1, 8)
        count = tdc.count_trading_days_between(start, end)
        assert count == 5

    def test_get_year_start_trading_day(self):
        """Test get_year_start_trading_day."""
        tdc = TradingDaysChina()
        start_day = tdc.get_year_start_trading_day(2023)
        # Should be the first trading day of 2023
        assert start_day.year == 2023
        assert start_day.month == 1
        assert start_day.weekday() < 5  # Should be a weekday

    def test_get_year_end_trading_day(self):
        """Test get_year_end_trading_day."""
        tdc = TradingDaysChina()
        end_day = tdc.get_year_end_trading_day(2023)
        # Should be the last trading day of 2023
        assert end_day.year == 2023
        assert end_day.month == 12
        assert end_day.weekday() < 5  # Should be a weekday


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_trading_days(self):
        """Test get_trading_days singleton."""
        tdc1 = get_trading_days()
        tdc2 = get_trading_days()
        assert tdc1 is tdc2

    def test_is_trading_day_function(self):
        """Test is_trading_day convenience function."""
        assert is_trading_day(date(2023, 1, 3)) is True
        assert is_trading_day(date(2023, 1, 7)) is False

    def test_get_nearest_trading_day_function(self):
        """Test get_nearest_trading_day convenience function."""
        result = get_nearest_trading_day(date(2023, 1, 7), prefer_backward=True)
        assert result.weekday() < 5

    def test_get_year_end_trading_day_function(self):
        """Test get_year_end_trading_day convenience function."""
        result = get_year_end_trading_day(2023)
        assert result.year == 2023
        assert result.month == 12

    def test_get_year_start_trading_day_function(self):
        """Test get_year_start_trading_day convenience function."""
        result = get_year_start_trading_day(2023)
        assert result.year == 2023
        assert result.month == 1
