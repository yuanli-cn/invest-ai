"""Tests for market models to boost coverage."""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from invest_ai.models import InvestmentType, PriceData
from invest_ai.market.models import (
    MarketDataCache,
    PriceFetcherConfig,
    MarketDataSummary,
    InvestmentInfo,
    PriceQuery,
)


class TestMarketDataCache:
    """Tests for MarketDataCache class."""

    def test_init(self):
        """Test initialization."""
        cache = MarketDataCache(ttl_seconds=1800)
        assert cache.ttl_seconds == 1800
        assert cache.cache == {}

    def test_generate_key(self):
        """Test _generate_key method."""
        cache = MarketDataCache()
        key = cache._generate_key("000001", date(2023, 1, 15), "tushare")
        assert key == "000001_2023-01-15_tushare"

    def test_set_and_get(self):
        """Test set and get methods."""
        cache = MarketDataCache()
        price = PriceData(
            code="000001",
            price_date=date(2023, 1, 15),
            price_value=10.50,
            source="tushare"
        )
        
        cache.set("000001", date(2023, 1, 15), "tushare", price)
        result = cache.get("000001", date(2023, 1, 15), "tushare")
        
        assert result is not None
        assert result.code == "000001"
        assert result.price_value == 10.50

    def test_get_expired(self):
        """Test get with expired data."""
        cache = MarketDataCache(ttl_seconds=0)  # Immediate expiry
        price = PriceData(
            code="000001",
            price_date=date(2023, 1, 15),
            price_value=10.50,
            source="tushare"
        )
        
        cache.set("000001", date(2023, 1, 15), "tushare", price)
        
        # Wait a tiny bit for expiry
        import time
        time.sleep(0.01)
        
        result = cache.get("000001", date(2023, 1, 15), "tushare")
        assert result is None

    def test_get_missing(self):
        """Test get with missing key."""
        cache = MarketDataCache()
        result = cache.get("000001", date(2023, 1, 15), "tushare")
        assert result is None

    def test_clear(self):
        """Test clear method."""
        cache = MarketDataCache()
        price = PriceData(
            code="000001",
            price_date=date(2023, 1, 15),
            price_value=10.50,
            source="tushare"
        )
        cache.set("000001", date(2023, 1, 15), "tushare", price)
        
        assert cache.size() == 1
        cache.clear()
        assert cache.size() == 0

    def test_size(self):
        """Test size method."""
        cache = MarketDataCache()
        assert cache.size() == 0
        
        for i in range(3):
            price = PriceData(
                code=f"00000{i}",
                price_date=date(2023, 1, 15),
                price_value=10.50,
                source="tushare"
            )
            cache.set(f"00000{i}", date(2023, 1, 15), "tushare", price)
        
        assert cache.size() == 3


class TestPriceFetcherConfig:
    """Tests for PriceFetcherConfig class."""

    def test_default_init(self):
        """Test default initialization."""
        config = PriceFetcherConfig()
        assert config.max_concurrent_requests == 10
        assert config.retry_attempts == 3
        assert config.retry_delay == 1.0
        assert config.timeout_seconds == 30
        assert config.validate_codes is True

    def test_custom_init(self):
        """Test custom initialization."""
        config = PriceFetcherConfig(
            max_concurrent_requests=5,
            retry_attempts=2,
            retry_delay=0.5,
            timeout_seconds=15,
            validate_codes=False
        )
        assert config.max_concurrent_requests == 5
        assert config.retry_attempts == 2
        assert config.retry_delay == 0.5
        assert config.timeout_seconds == 15
        assert config.validate_codes is False


class TestMarketDataSummary:
    """Tests for MarketDataSummary class."""

    def test_init(self):
        """Test initialization."""
        summary = MarketDataSummary()
        assert summary.data_sources == {}
        assert summary.successful_requests == 0
        assert summary.failed_requests == 0
        assert summary.total_codes == 0
        assert summary.missing_dates == 0

    def test_add_success(self):
        """Test add_success method."""
        summary = MarketDataSummary()
        summary.add_success("tushare")
        summary.add_success("tushare")
        summary.add_success("eastmoney")
        
        assert summary.successful_requests == 3
        assert summary.data_sources["tushare"] == 2
        assert summary.data_sources["eastmoney"] == 1

    def test_add_failure(self):
        """Test add_failure method."""
        summary = MarketDataSummary()
        summary.add_failure()
        summary.add_failure()
        
        assert summary.failed_requests == 2

    def test_set_total_codes(self):
        """Test set_total_codes method."""
        summary = MarketDataSummary()
        summary.set_total_codes(100)
        assert summary.total_codes == 100

    def test_add_missing_dates(self):
        """Test add_missing_dates method."""
        summary = MarketDataSummary()
        summary.add_missing_dates(5)
        summary.add_missing_dates()  # Default 1
        
        assert summary.missing_dates == 6

    def test_success_rate(self):
        """Test success_rate property."""
        summary = MarketDataSummary()
        summary.add_success("tushare")
        summary.add_success("tushare")
        summary.add_failure()
        
        # 2 / 3 = 0.666...
        assert abs(summary.success_rate - 0.6666666) < 0.01

    def test_success_rate_no_requests(self):
        """Test success_rate with no requests."""
        summary = MarketDataSummary()
        assert summary.success_rate == 0.0

    def test_completeness(self):
        """Test completeness property."""
        summary = MarketDataSummary()
        summary.set_total_codes(10)
        summary.add_success("tushare")
        summary.add_success("tushare")
        summary.add_success("tushare")
        
        assert summary.completeness == 0.3

    def test_completeness_no_codes(self):
        """Test completeness with no total codes."""
        summary = MarketDataSummary()
        assert summary.completeness == 0.0


class TestInvestmentInfo:
    """Tests for InvestmentInfo class."""

    def test_init(self):
        """Test initialization."""
        info = InvestmentInfo(
            code="000001",
            name="平安银行",
            investment_type=InvestmentType.STOCK,
            is_valid=True
        )
        assert info.code == "000001"
        assert info.name == "平安银行"
        assert info.investment_type == InvestmentType.STOCK
        assert info.is_valid is True
        assert info.market is None
        assert info.first_price_date is None
        assert info.last_price_date is None

    def test_str_with_name(self):
        """Test __str__ with name."""
        info = InvestmentInfo(code="000001", name="平安银行")
        result = str(info)
        assert "000001" in result
        assert "平安银行" in result
        assert "stock" in result

    def test_str_without_name(self):
        """Test __str__ without name."""
        info = InvestmentInfo(code="000001")
        result = str(info)
        assert "000001" in result

    def test_repr(self):
        """Test __repr__."""
        info = InvestmentInfo(code="000001", name="平安银行", is_valid=False)
        result = repr(info)
        assert "InvestmentInfo" in result
        assert "000001" in result
        assert "平安银行" in result
        assert "valid=False" in result


class TestPriceQuery:
    """Tests for PriceQuery class."""

    def test_init_sorts_data(self):
        """Test that init sorts codes and dates."""
        query = PriceQuery(
            codes=["000003", "000001", "000002"],
            dates=[date(2023, 3, 1), date(2023, 1, 1), date(2023, 2, 1)],
            investment_type=InvestmentType.STOCK
        )
        
        assert query.codes == ["000001", "000002", "000003"]
        assert query.dates == [date(2023, 1, 1), date(2023, 2, 1), date(2023, 3, 1)]

    def test_total_requests(self):
        """Test total_requests property."""
        query = PriceQuery(
            codes=["000001", "000002"],
            dates=[date(2023, 1, 1), date(2023, 2, 1), date(2023, 3, 1)],
            investment_type=InvestmentType.STOCK
        )
        
        # 2 codes * 3 dates = 6
        assert query.total_requests == 6

    def test_str(self):
        """Test __str__."""
        query = PriceQuery(
            codes=["000001", "000002"],
            dates=[date(2023, 1, 1), date(2023, 2, 1)],
            investment_type=InvestmentType.STOCK
        )
        
        result = str(query)
        assert "2 stocks" in result
        assert "2 dates" in result
        assert "4 requests" in result
