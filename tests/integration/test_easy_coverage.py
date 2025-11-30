"""
Easy coverage - test only basic instantiation and simple methods.
No complex mocking, just exercise public APIs.
"""

import pytest
from datetime import date

# Test basic imports work
def test_all_modules_import():
    """Test that all main modules can be imported."""
    import invest_ai
    assert invest_ai is not None

    from invest_ai import calculation, cli, config, market, models, reporting, transaction
    assert calculation is not None
    assert cli is not None
    assert config is not None
    assert market is not None
    assert models is not None
    assert reporting is not None
    assert transaction is not None


def test_market_clients_basic():
    """Test market client classes can be instantiated."""
    from invest_ai.market.stock_client import TushareClient
    from invest_ai.market.fund_client import EastMoneyClient
    from invest_ai.config import load_settings

    # EastMoney doesn't need token
    eastmoney = EastMoneyClient()
    assert eastmoney is not None

    # Tushare - behavior depends on token availability
    settings = load_settings()
    if settings.tushare_configured:
        # Token available, client should initialize
        tushare = TushareClient()
        assert tushare is not None
    else:
        # No token, should raise
        with pytest.raises(ValueError, match="Tushare token is required"):
            TushareClient()


def test_calculation_models():
    """Test calculation models."""
    from invest_ai.calculation.models import InvestmentType

    # Test enum
    assert hasattr(InvestmentType, 'STOCK')
    assert hasattr(InvestmentType, 'FUND')


def test_market_models_basic():
    """Test market model classes."""
    from invest_ai.market.models import PriceData

    price = PriceData(
        code="000001",
        price_date=date(2023, 11, 30),
        price_value=25.50,
        source="tushare",
    )
    assert price.code == "000001"
    assert price.price_value == 25.50


def test_models_basic():
    """Test main models."""
    from invest_ai.models import AnnualResult, HistoryResult, InvestmentType

    # Test AnnualResult
    annual = AnnualResult(
        code="000001",
        year=2023,
        start_value=1000.0,
        end_value=1250.0,
        net_gain=250.0,
        return_rate=25.0,
        dividends=50.0,
        capital_gain=200.0,
    )
    assert annual.code == "000001"
    assert annual.year == 2023

    # Test HistoryResult
    history = HistoryResult(
        code="000001",
        investment_type="stock",
        first_investment=date(2023, 1, 15),
        last_transaction=date(2023, 12, 31),
        total_invested=10000.0,
        current_value=12500.0,
        total_gain=2500.0,
        return_rate=25.0,
        realized_gains=1000.0,
        unrealized_gains=1500.0,
        dividend_income=500.0,
        transaction_count=5,
    )
    assert history.code == "000001"
    assert history.transaction_count == 5


def test_transaction_models():
    """Test transaction model classes."""
    from invest_ai.models import TransactionType

    assert TransactionType.BUY.value == "buy"
    assert TransactionType.SELL.value == "sell"
    assert TransactionType.DIVIDEND.value == "dividend"


def test_reporting_templates():
    """Test reporting template classes."""
    from invest_ai.reporting.templates import (
        AnnualReportTemplate,
        HistoryReportTemplate,
        ReportTemplate,
    )

    # Test template creation
    template = ReportTemplate()
    assert template.currency_symbol == "¥"

    annual_template = AnnualReportTemplate()
    assert annual_template is not None

    history_template = HistoryReportTemplate()
    assert history_template is not None


def test_reporting_tables():
    """Test reporting table classes."""
    from invest_ai.reporting.tables import TableFormatter

    formatter = TableFormatter()
    assert formatter is not None

    # Test static formatters
    assert "¥1,000.00" == TableFormatter.currency_formatter(1000.0)
    assert "+¥1,000.00" == TableFormatter.gain_loss_formatter(1000.0)


def test_reporting_errors():
    """Test reporting error classes."""
    from invest_ai.reporting.errors import (
        ErrorHandler,
        ErrorCollector,
        ReportingError,
        DataValidationError,
        FormattingError,
    )

    # Test error classes
    assert issubclass(ReportingError, Exception)
    assert issubclass(DataValidationError, ReportingError)
    assert issubclass(FormattingError, ReportingError)

    # Test handler
    handler = ErrorHandler()
    assert handler is not None

    # Test collector
    collector = ErrorCollector()
    assert collector is not None
    assert not collector.has_errors()


def test_transaction_filter():
    """Test transaction filter classes."""
    from invest_ai.transaction.filter import TransactionFilter

    filter_obj = TransactionFilter()
    assert filter_obj is not None


def test_transaction_loader():
    """Test transaction loader classes."""
    from invest_ai.transaction.loader import TransactionLoader

    loader = TransactionLoader()
    assert loader is not None


def test_transaction_validator():
    """Test transaction validator classes."""
    from invest_ai.transaction.validator import ValidationResult

    result = ValidationResult(is_valid=True, errors=[], warnings=[])
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_config_classes():
    """Test configuration classes."""
    from invest_ai.config.api_config import APIConfig
    from invest_ai.config.settings import Settings

    api_config = APIConfig()
    assert api_config is not None

    settings = Settings()
    assert settings is not None


def test_trading_days():
    """Test trading days module."""
    from invest_ai.market.trading_days import is_trading_day, get_trading_days, get_nearest_trading_day

    # Test functions exist
    assert callable(is_trading_day)
    assert callable(get_trading_days)
    assert callable(get_nearest_trading_day)