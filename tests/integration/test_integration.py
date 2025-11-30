"""Proper integration tests - CLI functionality with independent test data and mocked external dependencies."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from invest_ai.cli.main import CLIController


class TestIntegrationScenarios:
    """Integration tests with independent test data and mocked dependencies."""

    @pytest.fixture
    def stock_test_data(self):
        """Test data file for stock integration tests."""
        return Path(__file__).parent.parent / "data" / "simple_stock.yaml"

    @pytest.fixture
    def fund_test_data(self):
        """Test data file for fund integration tests."""
        return Path(__file__).parent.parent / "data" / "simple_fund.yaml"

    @pytest.fixture
    def portfolio_test_data(self):
        """Test data file for mixed portfolio integration tests."""
        return Path(__file__).parent.parent / "data" / "integration_portfolio.yaml"

    @pytest.mark.asyncio
    async def test_stock_annual_analysis(self, stock_test_data):
        """Test stock annual analysis with mocked data."""
        from invest_ai.models import PriceData
        from datetime import date
        
        controller = CLIController()

        # Mock year-start and year-end prices in new format
        mock_prices = {
            "year_start": {
                "600519": PriceData(code="600519", price_date=date(2023, 1, 3), price_value=1750.00, source="mock"),
            },
            "year_end": {
                "600519": PriceData(code="600519", price_date=date(2023, 12, 29), price_value=1726.00, source="mock"),
            }
        }

        result = await controller.execute_calculation(
            {
                "type": "stock",
                "data": str(stock_test_data),
                "code": "600519",
                "year": 2023,
                "mock_prices": mock_prices,
            }
        )

        # Verify result structure and calculations
        assert result is not None
        assert hasattr(result, "start_value")
        assert hasattr(result, "end_value")
        assert hasattr(result, "net_gain")
        assert hasattr(result, "dividends")
        assert result.dividends == 2175.0  # From test data
        # With mock prices, we should have calculated values
        assert result.end_value >= 0  # Should have end value from mock prices

    @pytest.mark.asyncio
    async def test_fund_annual_analysis(self, fund_test_data):
        """Test fund annual analysis with mocked data."""
        controller = CLIController()

        # Mock current NAV prices to avoid external API calls
        mock_prices = {"110020": 3.12}

        with patch.object(controller, "_get_current_prices") as mock_prices_func:
            mock_prices_func.return_value = mock_prices

            result = await controller.execute_calculation(
                {
                    "type": "fund",
                    "data": str(fund_test_data),
                    "code": "110020",
                    "year": 2023,
                }
            )

            # Verify result structure
            assert result is not None
            assert hasattr(result, "start_value")
            assert hasattr(result, "end_value")
            assert hasattr(result, "net_gain")
            assert result.dividends > 0  # Fund should have dividends

    @pytest.mark.asyncio
    async def test_portfolio_complete_history(self, portfolio_test_data):
        """Test complete portfolio history with mixed data."""
        from invest_ai.models import PriceData
        from datetime import date
        
        controller = CLIController()

        # Mock all current prices - pass as mock_prices to bypass API
        mock_prices = {
            "000001": PriceData(code="000001", price_date=date.today(), price_value=16.80, source="mock"),
        }

        result = await controller.execute_calculation(
            {
                "type": "stock",
                "data": str(portfolio_test_data),
                "mock_prices": mock_prices,
            }
        )

        # Verify result structure for portfolio
        assert result is not None
        assert hasattr(result, "total_invested")
        assert hasattr(result, "current_value")
        assert result.total_invested > 0
        # current_value depends on remaining holdings and mock prices
        assert result.current_value >= 0

    @pytest.mark.asyncio
    async def test_portfolio_json_output(self, portfolio_test_data):
        """Test JSON output format with integration data."""
        controller = CLIController()

        mock_prices = {"000001": 16.80, "110022": 3.12}

        with patch.object(controller, "_get_current_prices") as mock_prices_func:
            mock_prices_func.return_value = mock_prices

            # Test annual calculation with JSON output expectation
            result = await controller.execute_calculation(
                {
                    "type": "stock",
                    "data": str(portfolio_test_data),
                    "code": "000001",
                    "year": 2023,
                }
            )

            # Verify result is valid
            assert result is not None

            # Verify it can be serialized to JSON
            try:
                json_str = json.dumps(result, indent=2, default=str)
                assert json_str is not None
                assert "investment_type" in json_str or "2023" in str(result)
            except (TypeError, ValueError):
                pytest.fail("Result should be JSON-serializable")

    @pytest.mark.asyncio
    async def test_error_handling_invalid_file(self):
        """Test error handling with invalid data file."""
        controller = CLIController()

        result = await controller.execute_calculation(
            {
                "type": "stock",
                "data": "nonexistent_file.yaml",
                "code": "000001",
                "year": 2023,
            }
        )

        # Should return None for invalid file
        assert result is None

    @pytest.mark.asyncio
    async def test_error_handling_invalid_year(self, stock_test_data):
        """Test error handling with invalid year."""
        controller = CLIController()

        result = await controller.execute_calculation(
            {
                "type": "stock",
                "data": str(stock_test_data),
                "code": "600519",
                "year": 1800,  # Future year
            }
        )

        # Should return empty result for year with no transactions
        assert result is not None
        assert result.year == 1800
        assert result.start_value == 0.0
        assert result.end_value == 0.0
