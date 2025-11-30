"""Simple integration tests with realistic data."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from mock_data.api_responses import MockIntegrationTestData

from invest_ai.cli.main import CLIController


class TestSimpleRealScenarios:
    """Simple integration tests with realistic data."""

    @pytest.fixture
    def realistic_portfolio_file(self):
        """Integration test portfolio file."""
        return Path(__file__).parent.parent / "data" / "integration_portfolio.yaml"

    @pytest.mark.asyncio
    async def test_basic_portfolio_analysis(self, realistic_portfolio_file):
        """Test basic portfolio analysis with mocked prices."""
        controller = CLIController()

        # Mock current prices to avoid API calls
        mock_prices = {
            "000001": 16.80,  # Ping An Bank
            "110022": 3.12,  # Fund
        }

        with patch.object(controller, "_get_current_prices") as mock_prices_func:
            mock_prices_func.return_value = mock_prices

            # Test stock analysis
            result = await controller.execute_calculation(
                {
                    "type": "stock",
                    "data": str(realistic_portfolio_file),
                    "code": "000001",
                    "year": 2023,
                }
            )

            # Verify basic structure
            assert result is not None
            assert hasattr(result, "total_invested") or hasattr(result, "start_value")

    @pytest.mark.asyncio
    async def test_fund_portfolio_analysis(self, realistic_portfolio_file):
        """Test fund portfolio analysis."""
        controller = CLIController()

        mock_prices = {
            "110022": 3.12,  # Fund
        }

        with patch.object(controller, "_get_current_prices") as mock_prices_func:
            mock_prices_func.return_value = mock_prices

            # Test fund analysis
            result = await controller.execute_calculation(
                {
                    "type": "fund",
                    "data": str(realistic_portfolio_file),
                    "code": "110022",
                    "year": 2023,
                }
            )

            # Verify basic structure
            assert result is not None
            assert hasattr(result, "total_invested") or hasattr(result, "start_value")

    @pytest.mark.asyncio
    async def test_portfolio_json_output(self, realistic_portfolio_file):
        """Test JSON output format with realistic data."""
        controller = CLIController()

        mock_prices = {"000001": 16.80, "110022": 3.12}

        with patch.object(controller, "_get_current_prices") as mock_prices_func:
            mock_prices_func.return_value = mock_prices

            # Test JSON output
            result = await controller.execute_calculation(
                {
                    "type": "stock",
                    "data": str(realistic_portfolio_file),
                    "code": "000001",
                    "year": "2023",
                    "format": "json",
                }
            )

            # Verify JSON-serializable
            try:
                assert result is not None
                json_str = json.dumps(result, indent=2, default=str)
                assert json_str is not None
                assert "investment_type" in json_str or "2023" in json_str
            except (TypeError, ValueError):
                pytest.fail("Result should be JSON-serializable")

    @pytest.mark.asyncio
    async def test_complete_portfolio_valuation(self, realistic_portfolio_file):
        """Test complete portfolio valuation."""
        controller = CLIController()

        mock_prices = {
            "000001": 16.80,  # Ping An Bank
            "110022": 3.12,  # Fund
        }

        with patch.object(controller, "_get_current_prices") as mock_prices_func:
            mock_prices_func.return_value = mock_prices

            # Test complete portfolio
            result = await controller.execute_calculation(
                {"type": "stock", "data": str(realistic_portfolio_file)}
            )

            # Verify complete portfolio structure
            assert result is not None
            total_invested = (
                result.get("total_invested", 0)
                if hasattr(result, "get")
                else getattr(result, "total_invested", 0)
            )
            assert total_invested > 0

    def test_mock_api_response_validation(self):
        """Validate that mock API responses have correct structure."""
        # Test Tushare response structure
        tushare_response = MockIntegrationTestData.get_scenario_data()[
            "scenario_1_stock_analysis"
        ]
        tushare_api_data = tushare_response["mock_apis"]["tushare"]["daily"]

        assert "data" in tushare_api_data
        assert "items" in tushare_api_data["data"]
        assert tushare_api_data["code"] == 0

        if tushare_api_data["data"]["items"]:
            item = tushare_api_data["data"]["items"][0]
            required_fields = ["trade_date", "close", "open", "high", "low"]
            for field in required_fields:
                assert field in item
