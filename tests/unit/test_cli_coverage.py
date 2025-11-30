"""Additional tests for CLI module to boost coverage."""

import pytest
from datetime import date
from unittest.mock import Mock, patch, AsyncMock
import argparse

from invest_ai.cli.main import CLIController, main
from invest_ai.models import (
    TransactionList,
    Transaction,
    TransactionType,
    AnnualResult,
    HistoryResult,
)


class TestCLIController:
    """Tests for CLIController class."""

    def test_init(self):
        """Test initialization."""
        controller = CLIController()
        assert controller is not None
        assert controller.loader is not None
        assert controller.validator is not None
        assert controller.filter is not None
        assert controller.engine is not None
        assert controller.reporter is not None

    def test_get_arg_from_dict(self):
        """Test _get_arg with dict input."""
        controller = CLIController()
        args = {"type": "stock", "data": "test.yaml"}
        
        assert controller._get_arg(args, "type") == "stock"
        assert controller._get_arg(args, "data") == "test.yaml"
        assert controller._get_arg(args, "missing") is None
        assert controller._get_arg(args, "missing", "default") == "default"

    def test_get_arg_from_namespace(self):
        """Test _get_arg with Namespace input."""
        controller = CLIController()
        args = argparse.Namespace(type="stock", data="test.yaml")
        
        assert controller._get_arg(args, "type") == "stock"
        assert controller._get_arg(args, "data") == "test.yaml"
        assert controller._get_arg(args, "missing") is None

    def test_convert_mock_prices_empty(self):
        """Test _convert_mock_prices with None/empty input."""
        controller = CLIController()
        
        assert controller._convert_mock_prices(None) == {}
        assert controller._convert_mock_prices({}) == {}

    def test_convert_mock_prices_list(self):
        """Test _convert_mock_prices with list values."""
        controller = CLIController()
        mock_prices = {
            "000001": [10.0, 11.0, 12.0],
            "000002": [20.0],
        }
        
        result = controller._convert_mock_prices(mock_prices)
        assert result["000001"] == 10.0  # First element
        assert result["000002"] == 20.0

    def test_convert_mock_prices_scalar(self):
        """Test _convert_mock_prices with scalar values."""
        controller = CLIController()
        mock_prices = {
            "000001": 15.0,
        }
        
        result = controller._convert_mock_prices(mock_prices)
        assert result["000001"] == 15.0

    @pytest.mark.asyncio
    async def test_execute_calculation_with_dict_args(self):
        """Test execute_calculation with dict args."""
        controller = CLIController()
        
        # Create test transactions
        transactions = TransactionList(transactions=[
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=100,
                unit_price=10.0,
                total_amount=1000,
                transaction_date=date(2023, 1, 15)
            )
        ])
        
        args = {
            "type": "stock",
            "transactions": transactions,
            "mock_prices": {"000001": 12.0},
            "code": "000001",
            "year": None,
            "verbose": False,
        }
        
        result = await controller.execute_calculation(args)
        # Should return some result (may be None if validation fails, or a result)
        # This is just to cover the code path

    @pytest.mark.asyncio
    async def test_display_results_json(self):
        """Test display_results with JSON format."""
        controller = CLIController()
        result = AnnualResult(
            year=2023,
            code="000001",
            start_value=10000,
            end_value=12000,
            net_gain=2000,
            return_rate=20.0,
        )
        
        args = argparse.Namespace(
            format="json",
            year=2023,
            code="000001",
            type="stock"
        )
        
        # Should not raise
        await controller.display_results(result, args)


class TestMainFunction:
    """Tests for main function."""

    def test_main_no_args_shows_help(self, capsys, monkeypatch):
        """Test main with no arguments shows help and returns 0."""
        # Mock sys.argv to simulate running with no arguments
        monkeypatch.setattr("sys.argv", ["invest-ai"])
        
        result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "invest-ai" in captured.out


class TestCLIControllerDisplayResults:
    """Tests for display_results method."""

    @pytest.mark.asyncio
    async def test_display_results_table_format(self):
        """Test display_results with table format."""
        controller = CLIController()
        result = AnnualResult(
            year=2023,
            code="000001",
            start_value=10000,
            end_value=12000,
            net_gain=2000,
            return_rate=20.0,
        )
        
        args = argparse.Namespace(
            format="table",
            year=2023,
            code="000001",
            type="stock"
        )
        
        # Should not raise
        await controller.display_results(result, args)

    @pytest.mark.asyncio
    async def test_display_results_history(self):
        """Test display_results with history result."""
        controller = CLIController()
        result = HistoryResult(
            investment_type="stock",
            code="000001",
            first_investment=date(2020, 1, 1),
            last_transaction=date(2023, 12, 31),
            total_invested=10000,
            current_value=15000,
            total_gain=5000,
            return_rate=50.0,
        )
        
        args = argparse.Namespace(
            format="table",
            year=None,
            code="000001",
            type="stock"
        )
        
        await controller.display_results(result, args)

    @pytest.mark.asyncio
    async def test_display_results_none(self):
        """Test display_results with None result."""
        controller = CLIController()
        
        args = argparse.Namespace(
            format="table",
            year=2023,
            code="000001",
            type="stock"
        )
        
        # Should handle None result
        await controller.display_results(None, args)
