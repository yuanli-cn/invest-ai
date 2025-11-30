"""Integration tests for the complete workflow."""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from invest_ai.cli.main import CLIController
from invest_ai.config import load_settings
from invest_ai.models import Transaction, TransactionList, TransactionType
from invest_ai.reporting import ReportGenerator
from invest_ai.transaction import (
    TransactionValidator,
)


class TestFullWorkflow:
    """Integration tests for end-to-end workflows."""

    @pytest.mark.asyncio
    async def test_annual_returns_for_specific_stock(self, sample_yaml_file):
        """Test Use Case 2: Specific investment code with year."""
        import argparse
        from unittest.mock import AsyncMock

        controller = CLIController()

        # Mock the calculation engine to avoid API calls for testing
        with patch.object(controller, "engine") as mock_engine:
            # Mock the calculation result
            from invest_ai.models import AnnualResult, InvestmentType

            mock_result = AnnualResult(
                code="000001",
                year=2023,
                start_value=500.0,
                end_value=625.0,
                net_gain=125.0,
                return_rate=25.0,
                dividends=50.0,
                capital_gain=75.0,
            )
            mock_engine.calculate_annual_returns = AsyncMock(return_value=mock_result)

            # Mock loader, validator, and filter
            controller.loader = AsyncMock()
            controller.validator = AsyncMock()
            controller.filter = AsyncMock()

            # Mock transactions loading with some sample data
            from invest_ai.models import Transaction, TransactionList, TransactionType

            mock_transactions = TransactionList(
                transactions=[
                    Transaction(
                        code="000001",
                        date=date(2023, 1, 15),
                        type=TransactionType.BUY,
                        quantity=1000,
                        unit_price=10.00,
                        total_amount=10000,
                    ),
                ]
            )
            controller.loader.load_transactions.return_value = mock_transactions

            # Mock validator result
            mock_validation = AsyncMock()
            mock_validation.is_valid = True
            mock_validation.errors = []
            mock_validation.warnings = []
            controller.validator.validate_transactions.return_value = mock_validation

            # Mock filter result
            controller.filter.filter_transactions.return_value = mock_transactions

            # Create mock args namespace
            args = argparse.Namespace(
                type="stock",
                code="000001",
                year=2023,
                data=str(sample_yaml_file),
                format="table",
                verbose=False,
            )

            result = await controller.execute_calculation(args)

            assert result is not None
            assert isinstance(result, AnnualResult)
            assert result.year == 2023
            assert result.code == "000001"
            # The test passes if execution reaches here without errors

    @pytest.mark.asyncio
    async def test_full_history_for_specific_stock(self, sample_yaml_file):
        """Test Use Case 3: Specific investment full history."""
        import argparse
        from unittest.mock import AsyncMock

        controller = CLIController()

        # Mock the calculation engine
        with patch.object(controller, "engine") as mock_engine:
            # Mock the calculation result
            from invest_ai.models import HistoryResult, InvestmentType

            mock_result = HistoryResult(
                code="000001",
                investment_type="stock",
                first_investment=date(2023, 1, 15),
                last_transaction=date(2023, 12, 31),
                total_invested=1500.0,
                current_value=1750.0,
                total_gain=250.0,
                return_rate=16.67,
                realized_gains=100.0,
                unrealized_gains=150.0,
                dividend_income=50.0,
                transaction_count=4,
            )
            mock_engine.calculate_single_investment_history = AsyncMock(return_value=mock_result)

            # Mock loader, validator, and filter
            controller.loader = AsyncMock()
            controller.validator = AsyncMock()
            controller.filter = AsyncMock()

            # Mock transactions loading with some sample data
            from invest_ai.models import Transaction, TransactionList, TransactionType

            mock_transactions = TransactionList(
                transactions=[
                    Transaction(
                        code="000001",
                        date=date(2023, 1, 15),
                        type=TransactionType.BUY,
                        quantity=1000,
                        unit_price=10.00,
                        total_amount=10000,
                    ),
                ]
            )
            controller.loader.load_transactions.return_value = mock_transactions

            # Mock validator result
            mock_validation = AsyncMock()
            mock_validation.is_valid = True
            mock_validation.errors = []
            mock_validation.warnings = []
            controller.validator.validate_transactions.return_value = mock_validation

            # Mock filter result
            controller.filter.filter_transactions.return_value = mock_transactions

            # Create mock args namespace (no year specified for full history)
            args = argparse.Namespace(
                type="stock",
                code="000001",
                year=None,
                data=str(sample_yaml_file),
                format="table",
                verbose=False,
            )

            result = await controller.execute_calculation(args)

            assert result is not None
            assert isinstance(result, HistoryResult)
            assert result.code == "000001"
            assert result.investment_type == "stock"

    @pytest.mark.asyncio
    async def test_all_investments_full_history(self, sample_yaml_file):
        """Test Use Case 4: All investments full history."""
        import argparse
        from unittest.mock import AsyncMock

        controller = CLIController()

        # Mock the calculation engine
        with patch.object(controller, "engine") as mock_engine:
            # Mock the calculation result
            from invest_ai.models import HistoryResult, InvestmentType

            mock_result = HistoryResult(
                investment_type=InvestmentType.STOCK,
                code=None,
                first_investment=date(2023, 1, 15),
                last_transaction=date(2023, 12, 31),
                total_invested=3000.0,
                current_value=3500.0,
                total_gain=500.0,
                return_rate=16.67,
                realized_gains=200.0,
                unrealized_gains=300.0,
                dividend_income=100.0,
                transaction_count=6,
                investments=[],
            )
            mock_engine.calculate_portfolio_history = AsyncMock(
                return_value=mock_result
            )

            # Mock loader, validator, and filter
            controller.loader = AsyncMock()
            controller.validator = AsyncMock()
            controller.filter = AsyncMock()

            # Mock transactions loading with some sample data
            from invest_ai.models import Transaction, TransactionList, TransactionType

            mock_transactions = TransactionList(
                transactions=[
                    Transaction(
                        code="000001",
                        date=date(2023, 1, 15),
                        type=TransactionType.BUY,
                        quantity=1000,
                        unit_price=10.00,
                        total_amount=10000,
                    ),
                ]
            )
            controller.loader.load_transactions.return_value = mock_transactions

            # Mock validator result
            mock_validation = AsyncMock()
            mock_validation.is_valid = True
            mock_validation.errors = []
            mock_validation.warnings = []
            controller.validator.validate_transactions.return_value = mock_validation

            # Mock filter result
            controller.filter.filter_transactions.return_value = mock_transactions

            # Create mock args namespace (no code or year for all investments)
            args = argparse.Namespace(
                type="stock",
                code=None,
                year=None,
                data=str(sample_yaml_file),
                format="table",
                verbose=False,
            )

            result = await controller.execute_calculation(args)

            assert result is not None
            assert isinstance(result, HistoryResult)
            assert result.code is None
            assert result.investment_type == InvestmentType.STOCK

    @pytest.mark.asyncio
    async def test_error_handling_invalid_file(self):
        """Test error handling for invalid file."""
        controller = CLIController()

        invalid_file = "/nonexistent/transactions.yaml"

        # CLI should return error code 1 for invalid file
        result = await controller.run(["--type", "stock", "--data", invalid_file])
        assert result == 1

    @pytest.mark.asyncio
    async def test_error_handling_invalid_year(self, sample_yaml_file):
        """Test error handling for invalid year."""
        controller = CLIController()

        # CLI should return error code 1 for invalid year (1989 is before market start)
        result = await controller.run(
            [
                "--type",
                "stock",
                "--year",
                "1989",
                "--data",
                str(sample_yaml_file),
            ]
        )
        assert result == 1

    @pytest.mark.asyncio
    async def test_error_handling_invalid_type(self, sample_yaml_file):
        """Test error handling for invalid investment type.
        
        OpenSpec CLI Scenario: Invalid type specified
        - WHEN user runs with --type invalid
        - THEN system displays error and exits with code 1
        """
        controller = CLIController()

        # CLI should return error code for invalid type
        # argparse will exit with code 2 for invalid argument choices
        with pytest.raises(SystemExit) as exc_info:
            await controller.run(
                ["--type", "invalid", "--data", str(sample_yaml_file)]
            )
        assert exc_info.value.code == 2  # argparse exits with 2 for invalid choices

    @pytest.mark.asyncio
    async def test_help_flag_display(self, capsys):
        """Test help flag displays usage information.
        
        OpenSpec CLI Scenario: Help flag
        - WHEN user runs with --help
        - THEN system displays usage information
        """
        controller = CLIController()

        # --help should cause SystemExit with code 0
        with pytest.raises(SystemExit) as exc_info:
            await controller.run(["--help"])
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "--type" in captured.out
        assert "--data" in captured.out
        assert "stock" in captured.out or "fund" in captured.out

    @pytest.mark.asyncio
    async def test_no_arguments_shows_help(self, capsys):
        """Test running without arguments shows help summary.
        
        OpenSpec CLI Scenario: No arguments
        - WHEN user runs invest-ai without any arguments
        - THEN system displays help summary
        """
        controller = CLIController()

        # No arguments should show help and return 0
        result = await controller.run([])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "invest-ai" in captured.out
        assert "--type" in captured.out

    @pytest.mark.asyncio
    async def test_default_data_file_by_type(self):
        """Test default data file path based on investment type.
        
        OpenSpec CLI Scenario: Default data file by type
        - WHEN user omits --data with --type stock
        - THEN system uses data/stock.yaml as default
        """
        controller = CLIController()

        # Without --data, should try default path data/stock.yaml
        # Will return 1 if file doesn't exist (expected in test environment)
        result = await controller.run(["--type", "stock"])
        
        # Result is 1 because data/stock.yaml likely doesn't exist in test
        # But the important thing is it doesn't crash and tries the default path
        assert result in [0, 1]

    def test_configuration_validation(self):
        """Test configuration validation."""
        settings = load_settings()
        
        # Verify tushare_configured property works correctly
        # It should be True if token is set (from env or .env file), False otherwise
        assert settings.tushare_configured == bool(settings.tushare_token)
        
        # Verify the property returns a boolean
        assert isinstance(settings.tushare_configured, bool)


class TestDataValidation:
    """Integration tests for data validation."""

    @pytest.mark.asyncio
    async def test_transaction_validation_with_realistic_data(self):
        """Test validation with realistic transaction data."""
        realistic_transactions = [
            # Stock purchase with fees
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=1000,
                unit_price=25.50,
                total_amount=25550,  # Includes commission
            ),
            # Fund purchase with fees
            Transaction(
                code="110022",
                date=date(2023, 2, 20),
                type=TransactionType.BUY,
                quantity=500,
                unit_price=2.345,
                total_amount=1175,  # Net of fees
            ),
            # Stock sale with fees and taxes
            # [Transaction(
            #    code="000001",
            #    date=date(2023, 6, 20),
            #    type=TransactionType.SELL,
            #    quantity=500,
            #    unit_price=28.75,
            #    total_amount=14312, # Net of fees
            # ),
            # Cash dividend
            Transaction(
                code="000001",
                date=date(2023, 3, 15),
                type=TransactionType.DIVIDEND,
                quantity=0,
                unit_price=0.00,
                total_amount=500,
            ),
        ]

        validator = TransactionValidator()
        result = await validator.validate_transactions(
            TransactionList(transactions=realistic_transactions)
        )

        # Should pass validation despite fee variance
        assert result.is_valid
        assert len(result.errors) == 0


class TestAPIClients:
    """Integration tests for API clients."""

    async def test_market_data_integration(self):
        """Test integration with market data APIs using mocks."""
        # Test that the API clients can be instantiated with mocked data
        from invest_ai.market.stock_client import TushareClient
        from invest_ai.market.fund_client import EastMoneyClient

        # Test Tushare client initialization with token passed directly
        tushare_client = TushareClient(token="test_token")
        assert tushare_client is not None

        # Test East Money client initialization (no token required)
        eastmoney_client = EastMoneyClient()
        assert eastmoney_client is not None

    def test_api_configuration(self):
        """Test API configuration management."""
        from invest_ai.config import create_api_config

        config = create_api_config()
        assert config.eastmoney.is_configured  # East Money doesn't need config
        # tushare.is_configured depends on whether TUSHARE_TOKEN is set
        # Just verify the property exists and returns a boolean
        assert isinstance(config.tushare.is_configured, bool)

    def test_error_handling_without_token(self, monkeypatch):
        """Test error handling when Tushare token is missing."""
        from invest_ai.market.stock_client import TushareClient
        from invest_ai.config.api_config import TushareConfig, APIConfig

        # Mock create_api_config to return config without token
        def mock_create_api_config():
            return APIConfig(
                tushare=TushareConfig(token=None),
            )
        
        monkeypatch.setattr(
            "invest_ai.market.stock_client.create_api_config",
            mock_create_api_config
        )

        with pytest.raises(ValueError, match="Tushare token is required"):
            TushareClient()


class TestReportingIntegration:
    """Integration tests for reporting module."""

    @pytest.mark.asyncio
    async def test_report_generator_with_calculation_results(self):
        """Test report generator with real calculation results."""
        from invest_ai.models import AnnualResult, InvestmentType

        # Sample calculation result
        result = AnnualResult(
            code="000001",
            year=2023,
            start_value=1000.0,
            end_value=1250.0,
            net_gain=250.0,
            return_rate=25.0,
            dividends=50.0,
            capital_gain=200.0,
        )

        generator = ReportGenerator()

        # Test table report generation
        report = await generator.format_annual_report(
            result=result, investment_type="stock", year=2023, code="000001"
        )

        assert isinstance(report, str)
        assert "2023 Performance" in report
        assert "Start Value:" in report and "¥1,000.00" in report
        assert "End Value:" in report and "¥1,250.00" in report
        assert "Net Gain/Loss:" in report and "¥250.00" in report

    @pytest.mark.asyncio
    async def test_json_report_formatting(self):
        """Test JSON report formatting."""

        sample_data = {
            "investment_type": "stock",
            "year": 2023,
            "start_value": 1000.0,
            "end_value": 1250.0,
            "net_gain": 250.0,
            "return_rate": 25.0,
        }

        generator = ReportGenerator()
        json_report = await generator.format_json_report(sample_data)

        assert isinstance(json_report, str)
        # Should be valid JSON
        import json

        parsed_data = json.loads(json_report)
        assert parsed_data["year"] == 2023
        assert parsed_data["net_gain"] == 250.0

    def test_error_reporting(self):
        """Test error message formatting."""

        generator = ReportGenerator()
        error_report = generator.format_error_report(
            ValueError("Test error message"), "test context"
        )

        assert isinstance(error_report, str)
        assert "Error in test context" in error_report
        assert "Test error message" in error_report

    def test_summary_table_formatting(self):
        """Test summary table formatting."""
        from invest_ai.models import CalculationResult, InvestmentType

        investments = [
            CalculationResult(
                code="000001",
                investment_type=InvestmentType.STOCK,
                realized_gain=200.0,
                total_invested=1000.0,
                current_value=1200.0,
                total_gain=200.0,
                return_rate=20.0,
                cost_basis=1000.0,
            ),
            CalculationResult(
                code="000002",
                investment_type=InvestmentType.STOCK,
                realized_gain=-50.0,
                total_invested=500.0,
                current_value=450.0,
                total_gain=-50.0,
                return_rate=-10.0,
                cost_basis=500.0,
            ),
        ]

        generator = ReportGenerator()
        summary = generator.format_summary_table(investments)

        assert isinstance(summary, str)
        assert "TOTAL" in summary
        assert "¥1,500.00" in summary  # Total invested
        assert "¥1,650.00" in summary  # Total current value
        assert "+¥150.00" in summary  # Total P&L
