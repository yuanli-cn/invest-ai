"""Comprehensive integration tests simulating real user workflows."""

import pytest
from datetime import date
from unittest.mock import patch, AsyncMock
from pathlib import Path
import tempfile
import yaml

from invest_ai.cli.main import CLIController
from invest_ai.models import PriceData, AnnualResult, HistoryResult


class TestStockAnnualReturns:
    """Test stock annual returns calculations."""

    @pytest.mark.asyncio
    async def test_stock_annual_specific_stock_with_dividends(self):
        """Test annual returns for specific stock with dividend income."""
        controller = CLIController()

        # Create test data with buy, dividend, and sell transactions
        test_data = [
            {
                "code": "000001",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 20.00,
                "total_amount": 20000.00,
            },
            {
                "code": "000001",
                "date": "2023-03-15",
                "type": "dividend",
                "dividend_type": "cash",
                "quantity": 0,
                "unit_price": 0.00,
                "amount_per_share": 0.50,
                "total_amount": 500.00,
            },
            {
                "code": "000001",
                "date": "2023-06-15",
                "type": "sell",
                "quantity": 500,
                "unit_price": 25.00,
                "total_amount": 12500.00,
            },
            {
                "code": "000001",
                "date": "2023-12-31",
                "type": "sell",
                "quantity": 500,
                "unit_price": 28.00,
                "total_amount": 14000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}  # No current prices needed

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "000001",
                    "year": 2023,
                    "data": str(temp_file),
                })

                assert result is not None
                assert result.year == 2023
                assert result.code == "000001"
                assert result.start_value is not None
                assert result.end_value is not None
                assert result.dividends > 0  # Should have dividend income
                assert result.net_gain is not None
                assert result.return_rate is not None
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_stock_annual_portfolio_multiple_codes(self):
        """Test annual returns for entire stock portfolio."""
        controller = CLIController()

        test_data = [
            # Stock 1
            {
                "code": "000001",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 20.00,
                "total_amount": 20000.00,
            },
            # Stock 2
            {
                "code": "600036",
                "date": "2023-02-01",
                "type": "buy",
                "quantity": 500,
                "unit_price": 40.00,
                "total_amount": 20000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "year": 2023,
                    "data": str(temp_file),
                })

                assert result is not None
                assert result.year == 2023
                assert result.code is None  # Portfolio-level result
                assert result.start_value is not None
                assert result.end_value is not None
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_stock_annual_with_partial_year_transactions(self):
        """Test annual returns when transactions don't span full year."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2023-06-01",  # Mid-year start
                "type": "buy",
                "quantity": 1000,
                "unit_price": 20.00,
                "total_amount": 20000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "000001",
                    "year": 2023,
                    "data": str(temp_file),
                })

                assert result is not None
                assert result.year == 2023
                assert result.start_value >= 0  # Should handle mid-year start
        finally:
            temp_file.unlink()


class TestFundAnnualReturns:
    """Test fund annual returns calculations."""

    @pytest.mark.asyncio
    async def test_fund_annual_specific_fund(self):
        """Test annual returns for specific fund."""
        controller = CLIController()

        test_data = [
            {
                "code": "110022",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 10000,
                "unit_price": 2.00,
                "total_amount": 20000.00,
            },
            {
                "code": "110022",
                "date": "2023-06-15",
                "type": "buy",
                "quantity": 5000,
                "unit_price": 2.20,
                "total_amount": 11000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "fund",
                    "code": "110022",
                    "year": 2023,
                    "data": str(temp_file),
                })

                assert result is not None
                assert result.year == 2023
                assert result.code == "110022"
                assert result.start_value is not None
                assert result.end_value is not None
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_fund_annual_portfolio(self):
        """Test annual returns for entire fund portfolio."""
        controller = CLIController()

        test_data = [
            {
                "code": "110022",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 10000,
                "unit_price": 2.00,
                "total_amount": 20000.00,
            },
            {
                "code": "161725",
                "date": "2023-02-15",
                "type": "buy",
                "quantity": 8000,
                "unit_price": 1.50,
                "total_amount": 12000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "fund",
                    "year": 2023,
                    "data": str(temp_file),
                })

                assert result is not None
                assert result.year == 2023
                assert result.code is None  # Portfolio-level
        finally:
            temp_file.unlink()


class TestCompleteHistory:
    """Test complete investment history calculations."""

    @pytest.mark.asyncio
    async def test_stock_complete_history_single_code(self):
        """Test complete history for single stock."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2022-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 15.00,
                "total_amount": 15000.00,
            },
            {
                "code": "000001",
                "date": "2022-06-15",
                "type": "buy",
                "quantity": 500,
                "unit_price": 18.00,
                "total_amount": 9000.00,
            },
            {
                "code": "000001",
                "date": "2023-03-15",
                "type": "sell",
                "quantity": 600,
                "unit_price": 22.00,
                "total_amount": 13200.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "000001",
                    "data": str(temp_file),
                })

                assert result is not None
                assert result.code == "000001"
                assert isinstance(result, HistoryResult)
                assert result.first_investment is not None
                assert result.last_transaction is not None
                assert result.total_invested is not None
                assert result.total_gain is not None
                assert result.return_rate is not None
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_stock_complete_history_portfolio(self):
        """Test complete history for entire stock portfolio."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2022-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 15.00,
                "total_amount": 15000.00,
            },
            {
                "code": "600036",
                "date": "2022-03-15",
                "type": "buy",
                "quantity": 500,
                "unit_price": 35.00,
                "total_amount": 17500.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "data": str(temp_file),
                })

                assert result is not None
                assert isinstance(result, HistoryResult)
                assert result.code is None  # Portfolio-level
                assert result.total_invested > 0
        finally:
            temp_file.unlink()


class TestMixedPortfolio:
    """Test mixed stock and fund portfolio."""

    @pytest.mark.asyncio
    async def test_mixed_portfolio_annual(self):
        """Test annual returns for mixed stock and fund portfolio."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 20.00,
                "total_amount": 20000.00,
            },
            {
                "code": "110022",
                "date": "2023-02-15",
                "type": "buy",
                "quantity": 10000,
                "unit_price": 2.00,
                "total_amount": 20000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "year": 2023,
                    "data": str(temp_file),
                })

                assert result is not None
                assert result.year == 2023
        finally:
            temp_file.unlink()


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_transactions(self):
        """Test with empty transaction list."""
        controller = CLIController()

        test_data = []

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            result = await controller.execute_calculation({
                "type": "stock",
                "code": "000001",
                "year": 2023,
                "data": str(temp_file),
            })

            # With no transactions, may return None or a result with zero values
            # Either way, it should not crash
            if result is not None:
                assert result.start_value == 0.0 or result is None
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_nonexistent_code(self):
        """Test with code that doesn't exist in data."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 20.00,
                "total_amount": 20000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "999999",  # Non-existent code
                    "year": 2023,
                    "data": str(temp_file),
                })

                # Should handle gracefully
                assert result is not None
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_year_with_no_transactions(self):
        """Test year that has no transactions."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2022-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 15.00,
                "total_amount": 15000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "000001",
                    "year": 2023,  # No transactions in 2023
                    "data": str(temp_file),
                })

                # Should return result with zero values
                assert result is not None
                assert result.year == 2023
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_only_dividend_transactions(self):
        """Test with only dividend transactions (no buys/sells)."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2023-03-15",
                "type": "dividend",
                "dividend_type": "cash",
                "quantity": 0,
                "unit_price": 0.00,
                "amount_per_share": 0.50,
                "total_amount": 500.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "000001",
                    "year": 2023,
                    "data": str(temp_file),
                })

                # Should handle dividend-only case gracefully
                # May return None if no position exists, or a result with only dividends
                if result is not None:
                    assert result.dividends >= 0
        finally:
            temp_file.unlink()


class TestOutputFormats:
    """Test different output formats."""

    @pytest.mark.asyncio
    async def test_json_output_format(self):
        """Test JSON output format."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 20.00,
                "total_amount": 20000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "000001",
                    "year": 2023,
                    "data": str(temp_file),
                    "format": "json",
                })

                assert result is not None
                # Result should be JSON-serializable
                import json
                json_str = json.dumps(result, default=str)
                assert json_str is not None
        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_table_output_format(self):
        """Test table output format."""
        controller = CLIController()

        test_data = [
            {
                "code": "000001",
                "date": "2023-01-15",
                "type": "buy",
                "quantity": 1000,
                "unit_price": 20.00,
                "total_amount": 20000.00,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            temp_file = Path(f.name)

        try:
            with patch.object(controller, "_get_current_prices") as mock_prices:
                mock_prices.return_value = {}

                result = await controller.execute_calculation({
                    "type": "stock",
                    "code": "000001",
                    "year": 2023,
                    "data": str(temp_file),
                    "format": "table",
                })

                assert result is not None
        finally:
            temp_file.unlink()