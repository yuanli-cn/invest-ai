"""pytest configuration and fixtures."""

from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from invest_ai.models import (
    Transaction,
    TransactionType,
)


@pytest.fixture(autouse=True)
def mock_external_apis():
    """Auto-mock CLI price fetching to prevent real API access during tests.
    
    This fixture runs automatically for all tests to ensure:
    1. No real API calls are made from CLI
    2. Tests run fast
    3. Tests are deterministic
    
    Note: Individual tests can still mock specific API methods if needed.
    """
    from unittest.mock import patch, AsyncMock
    
    # Mock both price fetching methods - history mode and annual mode
    with patch(
        "invest_ai.cli.main.CLIController._fetch_current_prices_for_codes",
        new=AsyncMock(return_value={})
    ):
        with patch(
            "invest_ai.cli.main.CLIController._fetch_annual_prices",
            new=AsyncMock(return_value={"year_start": {}, "year_end": {}})
        ):
            yield


@pytest.fixture
def sample_transactions():
    """Sample transactions for testing."""
    return [
        Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=1000,
            unit_price=10.00,
            total_amount=10000,
        ),
        Transaction(
            code="000001",
            date=date(2023, 3, 20),
            type=TransactionType.BUY,
            quantity=500,
            unit_price=12.00,
            total_amount=6000,
        ),
        Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.SELL,
            quantity=700,
            unit_price=15.00,
            total_amount=10500,
        ),
        Transaction(
            code="000001",
            date=date(2023, 9, 10),
            type=TransactionType.DIVIDEND,
            quantity=0,
            unit_price=0.00,
            total_amount=500,
        ),
    ]


@pytest.fixture
def sample_fund_transactions():
    """Sample fund transactions for testing."""
    return [
        Transaction(
            code="110022",
            date=date(2023, 1, 10),
            type=TransactionType.BUY,
            quantity=1000,
            unit_price=2.345,
            total_amount=2345,
        ),
        Transaction(
            code="110022",
            date=date(2023, 12, 20),
            type=TransactionType.DIVIDEND,
            quantity=15.2,
            unit_price=0.00,
            total_amount=0,
        ),
    ]


@pytest.fixture
def sample_yaml_file(tmp_path):
    """Create a sample YAML transaction file."""
    yaml_content = """
- code: "000001"
  date: "2023-01-15"
  type: "buy"
  quantity: 1000
  unit_price: 10.00
  total_amount: 10000

- code: "000001"
  date: "2023-06-15"
  type: "sell"
  quantity: 500
  unit_price: 15.00
  total_amount: 7500

- code: "000001"
  date: "2023-03-15"
  type: "dividend"
  quantity: 0
  unit_price: 0.00
  total_amount: 500
"""

    file_path = tmp_path / "test_transactions.yaml"
    file_path.write_text(yaml_content)
    return file_path


@pytest.fixture
def test_data_dir():
    """Test data directory."""
    return Path(__file__).parent / "test_data"
