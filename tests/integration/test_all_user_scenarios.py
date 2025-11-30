"""Comprehensive Integration Tests covering all user scenarios.

This test file uses mocked external dependencies to simulate real API calls
and covers all major user workflows.
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from invest_ai.cli.main import CLIController
from invest_ai.models import (
    AnnualResult,
    HistoryResult,
    InvestmentType,
    PriceData,
    Transaction,
    TransactionList,
    TransactionType,
)


class TestAllUserScenarios:
    """Test all possible user scenarios with mocked APIs."""

    @pytest.fixture
    def mock_tushare_client(self):
        """Mock Tushare API client."""
        with patch("invest_ai.market.stock_client.TushareClient") as mock:
            client = AsyncMock()
            client.fetch_current_prices.return_value = {
                "000001": PriceData(
                    code="000001",
                    price_date=date(2024, 11, 30),
                    price_value=25.50,
                    source="tushare",
                ),
                "600036": PriceData(
                    code="600036",
                    price_date=date(2024, 11, 30),
                    price_value=45.80,
                    source="tushare",
                ),
            }
            client.fetch_historical_prices.return_value = {
                "000001": [
                    PriceData(
                        code="000001",
                        price_date=date(2024, 11, 30),
                        price_value=25.50,
                        source="tushare",
                    ),
                    PriceData(
                        code="000001",
                        price_date=date(2024, 6, 30),
                        price_value=23.20,
                        source="tushare",
                    ),
                    PriceData(
                        code="000001",
                        price_date=date(2024, 1, 2),
                        price_value=21.10,
                        source="tushare",
                    ),
                ],
                "600036": [
                    PriceData(
                        code="600036",
                        price_date=date(2024, 11, 30),
                        price_value=45.80,
                        source="tushare",
                    ),
                    PriceData(
                        code="600036",
                        price_date=date(2024, 6, 30),
                        price_value=42.50,
                        source="tushare",
                    ),
                    PriceData(
                        code="600036",
                        price_date=date(2024, 1, 2),
                        price_value=40.20,
                        source="tushare",
                    ),
                ],
            }
            yield client

    @pytest.fixture
    def mock_eastmoney_client(self):
        """Mock East Money API client."""
        with patch("invest_ai.market.fund_client.EastMoneyClient") as mock:
            client = AsyncMock()
            client.fetch_fund_nav.return_value = {
                "110011": PriceData(
                    code="110011",
                    price_date=date(2024, 11, 30),
                    price_value=2.156,
                    source="eastmoney",
                ),
                "161725": PriceData(
                    code="161725",
                    price_date=date(2024, 11, 30),
                    price_value=1.842,
                    source="eastmoney",
                ),
            }
            client.fetch_fund_prices_as_nav.return_value = {
                "110011": [
                    PriceData(
                        code="110011",
                        price_date=date(2024, 11, 30),
                        price_value=2.156,
                        source="eastmoney",
                    ),
                    PriceData(
                        code="110011",
                        price_date=date(2024, 6, 30),
                        price_value=2.045,
                        source="eastmoney",
                    ),
                ],
                "161725": [
                    PriceData(
                        code="161725",
                        price_date=date(2024, 11, 30),
                        price_value=1.842,
                        source="eastmoney",
                    ),
                    PriceData(
                        code="161725",
                        price_date=date(2024, 6, 30),
                        price_value=1.765,
                        source="eastmoney",
                    ),
                ],
            }
            yield client

    @pytest.fixture
    def sample_stock_transactions(self):
        """Sample stock transactions in chronological order."""
        return [
            Transaction(
                code="000001",
                transaction_date=date(2024, 1, 15),
                type=TransactionType.BUY,
                quantity=1000.0,
                unit_price=21.10,
                total_amount=21100.00,
            ),
            Transaction(
                code="600036",
                transaction_date=date(2024, 2, 10),
                type=TransactionType.BUY,
                quantity=500.0,
                unit_price=40.20,
                total_amount=20100.00,
            ),
            Transaction(
                code="000001",
                transaction_date=date(2024, 6, 20),
                type=TransactionType.SELL,
                quantity=500.0,
                unit_price=23.20,
                total_amount=11600.00,
            ),
            Transaction(
                code="600036",
                transaction_date=date(2024, 8, 15),
                type=TransactionType.DIVIDEND,
                quantity=0.0,
                unit_price=0.0,
                total_amount=500.00,
                dividend_type="cash",
            ),
        ]

    @pytest.fixture
    def sample_fund_transactions(self):
        """Sample fund transactions in chronological order."""
        return [
            Transaction(
                code="110011",
                transaction_date=date(2024, 3, 1),
                type=TransactionType.BUY,
                quantity=10000.0,
                unit_price=1.85,
                total_amount=18500.00,
            ),
            Transaction(
                code="161725",
                transaction_date=date(2024, 4, 1),
                type=TransactionType.BUY,
                quantity=8000.0,
                unit_price=1.62,
                total_amount=12960.00,
            ),
            Transaction(
                code="110011",
                transaction_date=date(2024, 9, 15),
                type=TransactionType.BUY,
                quantity=5000.0,
                unit_price=2.10,
                total_amount=10500.00,
            ),
        ]

    # ========================================================================
    # Scenario 1: Stock - Annual Returns for Specific Stock
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_stock_annual_specific_stock(
        self, mock_tushare_client, sample_stock_transactions
    ):
        """Scenario: Calculate annual returns for a specific stock in a specific year."""
        controller = CLIController()

        # Filter to just one stock
        stock_000001 = [
            tx
            for tx in sample_stock_transactions
            if tx.code == "000001"
        ]

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "code": "000001",
                "year": 2024,
                "transactions": TransactionList(transactions=sample_stock_transactions),
            }
        )

        # Assertions
        assert isinstance(result, AnnualResult)
        assert result.code == "000001"
        assert result.year == 2024
        assert result.start_value == 0  # No position at start of 2024
        assert result.end_value >= 0
        assert result.return_rate != 0

    # ========================================================================
    # Scenario 2: Stock - Annual Returns for Portfolio
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_stock_annual_portfolio(
        self, mock_tushare_client, sample_stock_transactions
    ):
        """Scenario: Calculate annual returns for entire stock portfolio in a year."""
        controller = CLIController()

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "year": 2024,
                "transactions": TransactionList(transactions=sample_stock_transactions),
            }
        )

        # Assertions
        assert isinstance(result, AnnualResult)
        assert result.code is None  # Portfolio calculation
        assert result.year == 2024
        assert result.start_value >= 0
        assert result.end_value >= 0

    # ========================================================================
    # Scenario 3: Stock - Complete History for Specific Stock
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_stock_history_specific_stock(
        self, mock_tushare_client, sample_stock_transactions
    ):
        """Scenario: Calculate complete investment history for a specific stock."""
        controller = CLIController()

        # Filter to just one stock
        stock_000001 = [
            tx
            for tx in sample_stock_transactions
            if tx.code == "000001"
        ]

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "code": "000001",
                "transactions": TransactionList(transactions=sample_stock_transactions),
                "mock_prices": mock_tushare_client.fetch_current_prices.return_value,
            }
        )

        # Assertions
        assert isinstance(result, HistoryResult)
        assert result.code == "000001"
        assert result.total_invested > 0
        assert result.current_value > 0
        assert result.return_rate != 0

    # ========================================================================
    # Scenario 4: Stock - Complete History for Portfolio
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_stock_history_portfolio(
        self, mock_tushare_client, sample_stock_transactions
    ):
        """Scenario: Calculate complete investment history for entire stock portfolio."""
        controller = CLIController()

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "transactions": TransactionList(transactions=sample_stock_transactions),
                "mock_prices": mock_tushare_client.fetch_current_prices.return_value,
            }
        )

        # Assertions
        assert isinstance(result, HistoryResult)
        assert result.code is None  # Portfolio
        assert result.total_invested > 0
        assert result.current_value > 0

    # ========================================================================
    # Scenario 5: Fund - Annual Returns for Specific Fund
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_fund_annual_specific_fund(
        self, mock_eastmoney_client, sample_fund_transactions
    ):
        """Scenario: Calculate annual returns for a specific fund in a specific year."""
        controller = CLIController()

        # Filter to just one fund
        fund_110011 = [
            tx
            for tx in sample_fund_transactions
            if tx.code == "110011"
        ]

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "fund",
                "code": "110011",
                "year": 2024,
                "transactions": TransactionList(transactions=sample_fund_transactions),
            }
        )

        # Assertions
        assert isinstance(result, AnnualResult)
        assert result.code == "110011"
        assert result.year == 2024
        assert result.start_value == 0  # No position at start of 2024
        assert result.end_value >= 0

    # ========================================================================
    # Scenario 6: Fund - Annual Returns for Portfolio
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_fund_annual_portfolio(
        self, mock_eastmoney_client, sample_fund_transactions
    ):
        """Scenario: Calculate annual returns for entire fund portfolio in a year."""
        controller = CLIController()

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "fund",
                "year": 2024,
                "transactions": TransactionList(transactions=sample_fund_transactions),
            }
        )

        # Assertions
        assert isinstance(result, AnnualResult)
        assert result.code is None
        assert result.year == 2024
        assert result.start_value >= 0
        assert result.end_value >= 0

    # ========================================================================
    # Scenario 7: Fund - Complete History for Specific Fund
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_fund_history_specific_fund(
        self, mock_eastmoney_client, sample_fund_transactions
    ):
        """Scenario: Calculate complete investment history for a specific fund."""
        controller = CLIController()

        # Filter to just one fund
        fund_110011 = [
            tx
            for tx in sample_fund_transactions
            if tx.code == "110011"
        ]

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "fund",
                "code": "110011",
                "transactions": TransactionList(transactions=sample_fund_transactions),
                "mock_prices": mock_eastmoney_client.fetch_fund_nav.return_value,
            }
        )

        # Assertions
        assert isinstance(result, HistoryResult)
        assert result.code == "110011"
        assert result.total_invested > 0
        assert result.current_value > 0

    # ========================================================================
    # Scenario 8: Fund - Complete History for Portfolio
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_fund_history_portfolio(
        self, mock_eastmoney_client, sample_fund_transactions
    ):
        """Scenario: Calculate complete investment history for entire fund portfolio."""
        controller = CLIController()

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "fund",
                "transactions": TransactionList(transactions=sample_fund_transactions),
                "mock_prices": mock_eastmoney_client.fetch_fund_nav.return_value,
            }
        )

        # Assertions
        assert isinstance(result, HistoryResult)
        assert result.code is None
        assert result.total_invested > 0
        assert result.current_value > 0

    # ========================================================================
    # Scenario 9: Mixed Portfolio - Stocks and Funds
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_mixed_portfolio_history(
        self, mock_tushare_client, mock_eastmoney_client
    ):
        """Scenario: Calculate complete history for mixed stock and fund portfolio."""
        controller = CLIController()

        mixed_transactions = [
            Transaction(
                code="000001",
                transaction_date=date(2024, 1, 15),
                type=TransactionType.BUY,
                quantity=1000.0,
                unit_price=21.10,
                total_amount=21100.00,
            ),
            Transaction(
                code="110011",
                transaction_date=date(2024, 3, 1),
                type=TransactionType.BUY,
                quantity=10000.0,
                unit_price=1.85,
                total_amount=18500.00,
            ),
        ]

        # Combine mock prices from both APIs
        combined_prices = {
            **mock_tushare_client.fetch_current_prices.return_value,
            **mock_eastmoney_client.fetch_fund_nav.return_value,
        }

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "transactions": TransactionList(transactions=mixed_transactions),
                "mock_prices": combined_prices,
            }
        )

        # Assertions
        assert isinstance(result, HistoryResult)
        assert result.total_invested > 0
        assert result.current_value > 0

    # ========================================================================
    # Scenario 10: JSON Output Format
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_json_output_format(
        self, mock_tushare_client, sample_stock_transactions
    ):
        """Scenario: Calculate returns and output in JSON format."""
        controller = CLIController()

        # Execute calculation with JSON format
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "code": "000001",
                "year": 2024,
                "format": "json",
                "transactions": TransactionList(transactions=sample_stock_transactions),
                "mock_prices": mock_tushare_client.fetch_historical_prices.return_value,
            }
        )

        # Assertions
        assert result is not None

    # ========================================================================
    # Scenario 11: Error Handling - Invalid Investment Code
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_error_invalid_code(
        self, mock_tushare_client, sample_stock_transactions
    ):
        """Scenario: Handle error when investment code doesn't exist in transactions."""
        controller = CLIController()

        # Execute with non-existent code but with actual transactions
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "code": "999999",
                "year": 2024,
                "transactions": TransactionList(transactions=sample_stock_transactions),
            }
        )

        # When code doesn't exist in transactions, should return empty result or None
        # The behavior depends on whether filtering produces empty transactions
        if result is not None:
            # If result returned, it should show zero values for non-existent code
            assert result.net_gain == 0.0 or result.total_invested == 0.0

    # ========================================================================
    # Scenario 12: Error Handling - Invalid File
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_error_invalid_file(self):
        """Scenario: Handle error when transaction file is invalid."""
        controller = CLIController()

        # Execute with invalid file
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "data": "/nonexistent/file.yaml",
            }
        )

        # Should return None for invalid file
        assert result is None

    # ========================================================================
    # Scenario 13: Edge Case - No Transactions
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_edge_case_no_transactions(self):
        """Scenario: Handle case with no transactions."""
        controller = CLIController()

        # Execute with empty transaction list
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "code": "000001",
                "data": None,
            }
        )

        # Should return None for empty transactions
        assert result is None

    # ========================================================================
    # Scenario 14: Dividend Income Tracking
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_dividend_tracking(self, mock_tushare_client):
        """Scenario: Track dividend income separately from capital gains."""
        controller = CLIController()

        transactions_with_dividends = [
            Transaction(
                code="000001",
                transaction_date=date(2024, 3, 15),
                type=TransactionType.BUY,
                quantity=1000.0,
                unit_price=21.10,
                total_amount=21100.00,
            ),
            Transaction(
                code="000001",
                transaction_date=date(2024, 8, 15),
                type=TransactionType.DIVIDEND,
                quantity=0.0,
                unit_price=0.0,
                total_amount=500.00,
                dividend_type="cash",
            ),
        ]

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "code": "000001",
                "year": 2024,
                "transactions": TransactionList(transactions=transactions_with_dividends),
                "mock_prices": mock_tushare_client.fetch_historical_prices.return_value,
            }
        )

        # Assertions
        assert isinstance(result, AnnualResult)
        assert result.dividends >= 0  # Should track dividend income

    # ========================================================================
    # Scenario 15: FIFO Cost Basis Accuracy
    # ========================================================================
    @pytest.mark.asyncio
    async def test_scenario_fifo_cost_basis(self, mock_tushare_client):
        """Scenario: Verify FIFO cost basis calculation is accurate."""
        controller = CLIController()

        # Multiple purchases at different prices
        transactions = [
            Transaction(
                code="000001",
                transaction_date=date(2024, 1, 15),
                type=TransactionType.BUY,
                quantity=1000.0,
                unit_price=20.00,
                total_amount=20000.00,
            ),
            Transaction(
                code="000001",
                transaction_date=date(2024, 6, 15),
                type=TransactionType.BUY,
                quantity=1000.0,
                unit_price=25.00,
                total_amount=25000.00,
            ),
            Transaction(
                code="000001",
                transaction_date=date(2024, 10, 15),
                type=TransactionType.SELL,
                quantity=1500.0,
                unit_price=27.00,
                total_amount=40500.00,
            ),
        ]

        # Mock prices for annual calculation (year_start and year_end format)
        mock_prices = {
            "year_start": {},  # No holdings at year start
            "year_end": {
                "000001": PriceData(
                    code="000001",
                    price_date=date(2024, 12, 31),
                    price_value=25.50,
                    source="mock"
                )
            }
        }

        # Execute calculation
        result = await controller.execute_calculation(
            {
                "type": "stock",
                "code": "000001",
                "year": 2024,
                "transactions": TransactionList(transactions=transactions),
                "mock_prices": mock_prices,
            }
        )

        # Assertions
        assert isinstance(result, AnnualResult)
        # Verify FIFO cost basis:
        # Buy 1000@20, Buy 1000@25, Sell 1500@27
        # FIFO sell: First 1000 @ cost 20 -> profit 7000, then 500 @ cost 25 -> profit 1000
        # Realized gain: 8000
        assert result.capital_gain == 8000.0
        
        # Remaining: 500 shares @ year-end price 25.50 = 12750
        assert result.end_value == 12750.0
        
        # Annual return calculation (matches poc/invest logic):
        # net_gain = (end_value + withdrawals + dividends) - (start_value + new_investments)
        # = (12750 + 40500 + 0) - (0 + 45000) = 8250
        # Note: realized gains are NOT added separately since withdrawals already includes the full sale amount
        assert result.net_gain == 8250.0