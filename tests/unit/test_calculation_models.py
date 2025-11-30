"""Tests for calculation models to boost coverage."""

import pytest
from datetime import date

from invest_ai.models import InvestmentType, PriceData
from invest_ai.calculation.models import (
    CalculationStatus,
    MarketDataRequirement,
    CalculationContext,
    PriceDataCache,
    PerformanceMetrics,
)


class TestCalculationStatus:
    """Tests for CalculationStatus enum."""

    def test_enum_values(self):
        """Test enum values exist."""
        assert CalculationStatus.PENDING == "pending"
        assert CalculationStatus.IN_PROGRESS == "in_progress"
        assert CalculationStatus.COMPLETED == "completed"
        assert CalculationStatus.FAILED == "failed"
        assert CalculationStatus.CANCELLED == "cancelled"


class TestMarketDataRequirement:
    """Tests for MarketDataRequirement class."""

    def test_init(self):
        """Test initialization."""
        req = MarketDataRequirement()
        assert req.required_dates == {}
        assert req.current_prices_needed == set()
        assert req.historical_prices_needed == set()

    def test_add_year_end_price_requirement(self):
        """Test add_year_end_price_requirement."""
        req = MarketDataRequirement()
        req.add_year_end_price_requirement("000001", 2023)
        
        assert "000001" in req.required_dates
        assert len(req.required_dates["000001"]) == 1

    def test_add_year_start_price_requirement(self):
        """Test add_year_start_price_requirement."""
        req = MarketDataRequirement()
        req.add_year_start_price_requirement("000001", 2023)
        
        assert "000001" in req.required_dates
        assert len(req.required_dates["000001"]) == 1

    def test_add_current_price_requirement(self):
        """Test add_current_price_requirement."""
        req = MarketDataRequirement()
        req.add_current_price_requirement("000001")
        
        assert "000001" in req.current_prices_needed

    def test_get_unique_dates(self):
        """Test get_unique_dates."""
        req = MarketDataRequirement()
        req.required_dates = {
            "000001": [date(2023, 1, 1), date(2023, 12, 29)],
            "000002": [date(2023, 1, 1), date(2023, 6, 30)],
        }
        
        unique = req.get_unique_dates()
        assert len(unique) == 3  # 3 unique dates

    def test_get_required_codes(self):
        """Test get_required_codes."""
        req = MarketDataRequirement()
        req.required_dates = {"000001": [date(2023, 1, 1)]}
        req.current_prices_needed = {"000002", "000003"}
        
        codes = req.get_required_codes()
        assert codes == {"000001", "000002", "000003"}


class TestCalculationContext:
    """Tests for CalculationContext class."""

    def test_init(self):
        """Test initialization."""
        ctx = CalculationContext(
            investment_type=InvestmentType.STOCK,
            year=2023,
            specific_code="000001",
            calculation_type="annual"
        )
        
        assert ctx.investment_type == InvestmentType.STOCK
        assert ctx.year == 2023
        assert ctx.specific_code == "000001"
        assert ctx.calculation_type == "annual"
        assert ctx.status == CalculationStatus.PENDING
        assert ctx.created_at == date.today()
        assert ctx.completed_at is None
        assert ctx.error_message is None

    def test_mark_in_progress(self):
        """Test mark_in_progress."""
        ctx = CalculationContext(investment_type=InvestmentType.STOCK)
        ctx.mark_in_progress()
        
        assert ctx.status == CalculationStatus.IN_PROGRESS

    def test_mark_completed(self):
        """Test mark_completed."""
        ctx = CalculationContext(investment_type=InvestmentType.STOCK)
        ctx.mark_completed()
        
        assert ctx.status == CalculationStatus.COMPLETED
        assert ctx.completed_at == date.today()

    def test_mark_failed(self):
        """Test mark_failed."""
        ctx = CalculationContext(investment_type=InvestmentType.STOCK)
        ctx.mark_failed("Test error")
        
        assert ctx.status == CalculationStatus.FAILED
        assert ctx.error_message == "Test error"
        assert ctx.completed_at == date.today()

    def test_is_complete_false(self):
        """Test is_complete when not complete."""
        ctx = CalculationContext(investment_type=InvestmentType.STOCK)
        assert ctx.is_complete is False
        
        ctx.mark_in_progress()
        assert ctx.is_complete is False

    def test_is_complete_true(self):
        """Test is_complete when complete."""
        ctx = CalculationContext(investment_type=InvestmentType.STOCK)
        ctx.mark_completed()
        assert ctx.is_complete is True

        ctx2 = CalculationContext(investment_type=InvestmentType.STOCK)
        ctx2.mark_failed("Error")
        assert ctx2.is_complete is True

    def test_duration_days(self):
        """Test duration_days property."""
        ctx = CalculationContext(investment_type=InvestmentType.STOCK)
        assert ctx.duration_days is None
        
        ctx.mark_completed()
        assert ctx.duration_days == 0  # Same day


class TestPriceDataCache:
    """Tests for PriceDataCache class."""

    def test_init(self):
        """Test initialization."""
        cache = PriceDataCache()
        assert cache.cache == {}

    def test_add_price_data(self):
        """Test add_price_data."""
        cache = PriceDataCache()
        price = PriceData(
            code="000001",
            price_date=date(2023, 1, 15),
            price_value=10.50,
            source="tushare"
        )
        cache.add_price_data("000001", price)
        
        assert "000001" in cache.cache
        assert price.price_date in cache.cache["000001"]

    def test_get_price_data(self):
        """Test get_price_data."""
        cache = PriceDataCache()
        price = PriceData(
            code="000001",
            price_date=date(2023, 1, 15),
            price_value=10.50,
            source="tushare"
        )
        cache.add_price_data("000001", price)
        
        result = cache.get_price_data("000001", price.price_date)
        assert result is not None
        assert result.price_value == 10.50
        
        # Missing
        result = cache.get_price_data("000002", price.price_date)
        assert result is None

    def test_get_latest_price_data(self):
        """Test get_latest_price_data."""
        cache = PriceDataCache()
        p1 = PriceData(code="000001", price_date=date(2023, 1, 1), price_value=10.0, source="tushare")
        p2 = PriceData(code="000001", price_date=date(2023, 6, 1), price_value=12.0, source="tushare")
        p3 = PriceData(code="000001", price_date=date(2023, 3, 1), price_value=11.0, source="tushare")
        
        cache.add_price_data("000001", p1)
        cache.add_price_data("000001", p2)
        cache.add_price_data("000001", p3)
        
        latest = cache.get_latest_price_data("000001")
        assert latest is not None
        assert latest.price_date == date(2023, 6, 1)
        assert latest.price_value == 12.0

    def test_get_latest_price_data_empty(self):
        """Test get_latest_price_data with empty cache."""
        cache = PriceDataCache()
        assert cache.get_latest_price_data("000001") is None

    def test_clear(self):
        """Test clear."""
        cache = PriceDataCache()
        price = PriceData(
            code="000001",
            price_date=date(2023, 1, 15),
            price_value=10.50,
            source="tushare"
        )
        cache.add_price_data("000001", price)
        
        cache.clear()
        assert cache.cache == {}

    def test_size(self):
        """Test size."""
        cache = PriceDataCache()
        assert cache.size() == 0
        
        p1 = PriceData(code="000001", price_date=date(2023, 1, 1), price_value=10.0, source="tushare")
        p2 = PriceData(code="000001", price_date=date(2023, 2, 1), price_value=11.0, source="tushare")
        p3 = PriceData(code="000002", price_date=date(2023, 1, 1), price_value=20.0, source="tushare")
        
        cache.add_price_data("000001", p1)
        cache.add_price_data("000001", p2)
        cache.add_price_data("000002", p3)
        
        assert cache.size() == 3


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics class."""

    def test_init(self):
        """Test initialization."""
        metrics = PerformanceMetrics()
        assert metrics.api_calls_made == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.calculation_time_ms == 0
        assert metrics.data_fetch_time_ms == 0

    def test_timing(self):
        """Test start_timing and end_timing."""
        metrics = PerformanceMetrics()
        
        metrics.start_timing()
        import time
        time.sleep(0.01)  # 10ms
        metrics.end_timing()
        
        assert metrics.calculation_time_ms >= 10

    def test_total_time_ms(self):
        """Test total_time_ms property."""
        metrics = PerformanceMetrics()
        metrics.calculation_time_ms = 100
        metrics.data_fetch_time_ms = 50
        
        assert metrics.total_time_ms == 150

    def test_cache_hit_rate(self):
        """Test cache_hit_rate property."""
        metrics = PerformanceMetrics()
        metrics.cache_hits = 7
        metrics.cache_misses = 3
        
        assert metrics.cache_hit_rate == 0.7

    def test_cache_hit_rate_no_requests(self):
        """Test cache_hit_rate with no requests."""
        metrics = PerformanceMetrics()
        assert metrics.cache_hit_rate == 0.0
