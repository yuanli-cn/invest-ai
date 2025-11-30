"""Tests for calculation engine (FIFO, annual, history)."""

from datetime import date

import pytest

from invest_ai.calculation import AnnualCalculator, FifoCalculator, HistoryCalculator
from invest_ai.models import (
    InvestmentType,
    PriceData,
    Transaction,
    TransactionList,
    TransactionType,
)


class TestFifoCalculator:
    """Test FIFO cost allocation."""

    def test_process_fifo_queue(self):
        """Test processing transactions into FIFO queue."""
        transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 2, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=12.00,
                total_amount=600.00,
            ),
        ]

        calculator = FifoCalculator()
        queue = calculator.process_fifo_queue(transactions)

        assert len(queue.purchases) == 2
        assert queue.total_quantity == 150.0
        assert queue.has_inventory

        # Check FIFO order (earliest first)
        assert queue.purchases[0].date == date(2023, 1, 15)
        assert queue.purchases[1].date == date(2023, 2, 15)

    def test_process_fifo_with_dividends(self):
        """Test FIFO processing with dividend transactions."""
        transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 3, 15),
                type=TransactionType.DIVIDEND,
                quantity=10.0,
                unit_price=0.00,
                total_amount=0.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 2, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=12.00,
                total_amount=600.00,
            ),
        ]

        calculator = FifoCalculator()
        queue = calculator.process_fifo_queue(transactions)

        assert len(queue.purchases) == 3
        assert queue.total_quantity == 160.0
        # Check purchase with zero unit price (dividend)
        dividend_purchase = next(p for p in queue.purchases if p.unit_price == 0.0)
        assert dividend_purchase.quantity == 10.0

    def test_allocate_cost_full_sale(self):
        """Test allocating cost for a full sale."""
        # Setup FIFO queue
        transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 2, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=12.00,
                total_amount=600.00,
            ),
        ]

        calculator = FifoCalculator()
        queue = calculator.process_fifo_queue(transactions)

        sell_transaction = Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.SELL,
            quantity=120.0,
            unit_price=15.00,
            total_amount=1800.00,
        )

        fifo_result = calculator.allocate_cost(sell_transaction, queue)

        assert fifo_result.cost_basis == 1240.00  # 100*10 + 20*12
        assert len(fifo_result.allocated_purchases) == 2
        assert fifo_result.remaining_queue.total_quantity == 30.0

    def test_allocate_cost_partial_sale(self):
        """Test allocating cost for a partial sale."""
        transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 2, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=12.00,
                total_amount=600.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 3, 15),
                type=TransactionType.BUY,
                quantity=75.0,
                unit_price=11.00,
                total_amount=825.00,
            ),
        ]

        calculator = FifoCalculator()
        queue = calculator.process_fifo_queue(transactions)

        sell_transaction = Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=15.00,
            total_amount=750.00,
        )

        fifo_result = calculator.allocate_cost(sell_transaction, queue)

        assert fifo_result.cost_basis == 500.00  # 50*10
        assert len(fifo_result.allocated_purchases) == 1
        assert fifo_result.remaining_queue.total_quantity == 175.0

    def test_allocate_cost_insufficient_inventory(self):
        """Test allocating cost when inventory is insufficient."""
        transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=10.00,
                total_amount=500.00,
            ),
        ]

        calculator = FifoCalculator()
        queue = calculator.process_fifo_queue(transactions)

        sell_transaction = Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.SELL,
            quantity=100.0,
            unit_price=15.00,
            total_amount=1500.00,
        )

        with pytest.raises(ValueError, match="Insufficient inventory"):
            calculator.allocate_cost(sell_transaction, queue)

    def test_calculate_realized_gain(self):
        """Test realized gain calculation."""
        calculator = FifoCalculator()

        # Profit scenario
        sell_transaction = Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=15.00,
            total_amount=750.00,
        )

        cost_basis = 500.00  # Bought at 10.00
        realized_gain = calculator.calculate_realized_gain(sell_transaction, cost_basis)

        assert realized_gain == 250.00  # 750 - 500

        # Loss scenario
        loss_transaction = Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=8.00,
            total_amount=400.00,
        )

        cost_basis = 500.00
        realized_loss = calculator.calculate_realized_gain(loss_transaction, cost_basis)

        assert realized_loss == -100.00  # 400 - 500

    def test_validate_fifo_processing(self):
        """Test FIFO processing validation."""
        # Valid transactions
        valid_transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 2, 15),
                type=TransactionType.SELL,
                quantity=30.00,
                unit_price=15.00,
                total_amount=450.00,
            ),
        ]

        calculator = FifoCalculator()
        errors = calculator.validate_fifo_processing(valid_transactions)
        assert len(errors) == 0

        # Invalid transactions (negative position)
        invalid_transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=10.00,
                total_amount=500.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 2, 15),
                type=TransactionType.SELL,
                quantity=75.0,
                unit_price=15.00,
                total_amount=1125.00,
            ),
        ]

        errors = calculator.validate_fifo_processing(invalid_transactions)
        assert len(errors) > 0
        assert "Negative position" in errors[0]


class TestAnnualCalculator:
    """Test annual return calculation."""

    def test_calculate_new_investments(self):
        """Test calculating new investments during a year."""
        year_transactions = [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000002",
                date=date(2023, 6, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=20.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000003",
                date=date(2023, 9, 15),
                type=TransactionType.BUY,
                quantity=25.0,
                unit_price=40.00,
                total_amount=1000.00,
            ),
        ]

        calculator = AnnualCalculator()
        new_investments = calculator.calculate_new_investments(
            TransactionList(transactions=year_transactions)
        )

        assert new_investments == 3000.00

    def test_calculate_dividend_income(self):
        """Test calculating dividend income."""
        year_transactions = [
            Transaction(
                code="000001",
                date=date(2023, 3, 15),
                type=TransactionType.DIVIDEND,
                quantity=0.0,
                unit_price=0.00,
                total_amount=200.00,
            ),
            Transaction(
                code="000002",
                date=date(2023, 6, 15),
                type=TransactionType.DIVIDEND,
                quantity=0.0,
                unit_price=0.00,
                total_amount=150.00,
            ),
        ]

        calculator = AnnualCalculator()
        dividend_income = calculator.calculate_dividend_income(
            TransactionList(transactions=year_transactions)
        )

        assert dividend_income == 350.00


class TestHistoryCalculator:
    """Test history calculation."""

    def setup_sample_data(self):
        """Setup sample transaction data."""
        return [
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 3, 15),
                type=TransactionType.DIVIDEND,
                quantity=0.0,
                unit_price=0.00,
                total_amount=100.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 6, 15),
                type=TransactionType.SELL,
                quantity=50.0,
                unit_price=15.00,
                total_amount=750.00,
            ),
            Transaction(
                code="000002",
                date=date(2023, 2, 15),
                type=TransactionType.BUY,
                quantity=200.0,
                unit_price=5.00,
                total_amount=1000.00,
            ),
        ]

    def test_calculate_total_invested(self):
        """Test calculating total invested amount."""
        calculator = HistoryCalculator()
        total = calculator.calculate_total_invested(
            TransactionList(transactions=self.setup_sample_data())
        )

        assert total == 2000.00  # 1000 + 1000

    def test_calculate_dividend_income(self):
        """Test calculating dividend income."""
        calculator = HistoryCalculator()
        dividend_income = calculator.calculate_dividend_income(
            TransactionList(transactions=self.setup_sample_data())
        )

        assert dividend_income == 100.00

    def test_calculate_code_current_value(self):
        """Test calculating current value for specific code."""
        calculator = HistoryCalculator()

        # Mock current prices
        current_prices = {
            "000001": PriceData(
                code="000001",
                price_date=date(2023, 12, 31),
                price_value=12.50,
                source="test",
            )
        }

        transactions = TransactionList(transactions=self.setup_sample_data())
        current_value = calculator.calculate_code_current_value(
            transactions, "000001", current_prices
        )

        # 100 shares bought - 50 sold = 50 remaining × 12.50
        assert current_value == 625.0

    def test_calculate_code_gains(self):
        """Test calculating gains for specific code."""
        calculator = HistoryCalculator()

        # Mock current prices
        sell_gain = 250.00
        unrealized_gain = 125.00  # 625 - 500

        transactions = TransactionList(transactions=self.setup_sample_data())
        current_prices = {
            "000001": PriceData(
                code="000001",
                price_date=date(2023, 12, 31),
                price_value=12.50,
                source="test",
            )
        }

        realized, unrealized = calculator.calculate_code_gains(
            transactions, "000001", current_prices
        )

        assert realized == sell_gain
        assert unrealized == unrealized_gain

    @pytest.mark.asyncio
    async def test_calculate_complete_history(self):
        """Test complete history calculation."""
        calculator = HistoryCalculator()

        # Mock current prices
        current_prices = {
            "000001": PriceData(
                code="000001",
                price_date=date(2023, 12, 31),
                price_value=12.50,
                source="test",
            )
        }

        transactions = TransactionList(transactions=self.setup_sample_data())
        result = await calculator.calculate_complete_history(
            transactions, current_prices
        )

        assert result.investment_type == InvestmentType.STOCK
        assert result.first_investment == date(2023, 1, 15)
        assert result.last_transaction == date(2023, 6, 15)
        assert result.total_invested == 2000.00
        assert result.transaction_count == 4
        assert result.code is None  # Portfolio calculation

    @pytest.mark.asyncio
    async def test_calculate_single_investment_history(self):
        """Test single investment history calculation."""
        calculator = HistoryCalculator()

        # Mock current prices
        current_prices = {
            "000001": PriceData(
                code="000001",
                price_date=date(2023, 12, 31),
                price_value=12.50,
                source="test",
            )
        }

        transactions = TransactionList(
            transactions=self.setup_sample_data()
        ).filter_by_code("000001")
        result = await calculator.calculate_single_investment_history(
            transactions, "000001", current_prices
        )

        assert result.code == "000001"
        assert result.investment_type == InvestmentType.STOCK
        assert result.total_invested == 1000.00
        assert len(result.investments) == 1

    @pytest.mark.asyncio
    async def test_calculate_portfolio_history(self):
        """Test portfolio history calculation."""
        calculator = HistoryCalculator()

        # Mock current prices for all codes
        current_prices = {
            "000001": PriceData(
                code="000001",
                price_date=date(2023, 12, 31),
                price_value=12.50,
                source="test",
            ),
            "000002": PriceData(
                code="000002",
                price_date=date(2023, 12, 31),
                price_value=6.00,
                source="test",
            ),
        }

        transactions = TransactionList(transactions=self.setup_sample_data())
        result = await calculator.calculate_portfolio_history(
            transactions, current_prices
        )

        assert result.code is None  # Portfolio calculation
        assert len(result.investments) == 2  # 000001, 000002
