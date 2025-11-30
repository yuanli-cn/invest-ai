"""Tests for data models."""

from datetime import date

import pytest
from pydantic import ValidationError

from invest_ai.models import (
    FifoQueue,
    HoldingsResult,
    InvestmentType,
    Purchase,
    Transaction,
    TransactionList,
    TransactionType,
    ValidationResult,
)


class TestTransaction:
    """Test Transaction model."""

    def test_valid_buy_transaction(self):
        """Test creating a valid buy transaction."""
        tx = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.50,
            total_amount=1050.00,
        )
        assert tx.code == "000001"
        assert tx.type == TransactionType.BUY
        assert tx.quantity == 100.0
        assert tx.unit_price == 10.50
        assert tx.total_amount == 1050.00

    def test_valid_sell_transaction(self):
        """Test creating a valid sell transaction."""
        tx = Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=15.00,
            total_amount=750.00,
        )
        assert tx.code == "000001"
        assert tx.type == TransactionType.SELL
        assert tx.quantity == 50.0
        assert tx.unit_price == 15.00
        assert tx.total_amount == 750.00

    def test_valid_cash_dividend(self):
        """Test creating a valid cash dividend transaction."""
        tx = Transaction(
            code="000001",
            date=date(2023, 3, 15),
            type=TransactionType.DIVIDEND,
            quantity=0.0,
            unit_price=0.00,
            total_amount=500.00,
        )
        assert tx.code == "000001"
        assert tx.type == TransactionType.DIVIDEND
        assert tx.total_amount == 500.00
        # Cash dividend indicated by quantity=0, total_amount>0

    def test_valid_stock_dividend(self):
        """Test creating a valid stock dividend transaction."""
        tx = Transaction(
            code="000001",
            date=date(2023, 6, 15),
            type=TransactionType.DIVIDEND,
            quantity=50.0,
            unit_price=0.00,
            total_amount=0.00,
        )
        assert tx.quantity == 50.0
        assert tx.unit_price == 0.00
        assert tx.total_amount == 0.00
        # Stock dividend indicated by quantity>0, total_amount=0

    def test_transaction_type_validation(self):
        """Test transaction type validation."""
        with pytest.raises(ValidationError):
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type="invalid_type",
                quantity=100.0,
                unit_price=10.50,
                total_amount=1050.00,
            )

    def test_code_validation(self):
        """Test investment code validation."""
        # Valid 6-digit codes
        assert (
            Transaction(
                code="000001",
                date=date(2023, 1, 15),
                type=TransactionType.BUY,
                quantity=100.0,
                unit_price=10.50,
                total_amount=1050.00,
            ).code
            == "000001"
        )

        # Various code formats (no strict validation in simplified model)
        tx_short = Transaction(
            code="abc123",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.50,
            total_amount=1050.00,
        )
        assert tx_short.code == "abc123"

        # Short code format (no strict validation)
        tx_short_code = Transaction(
            code="123",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.50,
            total_amount=1050.00,
        )
        assert tx_short_code.code == "123"

    def test_investment_type_detection(self):
        """Test investment type detection."""
        # Stock code (starts with 6)
        stock_tx = Transaction(
            code="600000",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.50,
            total_amount=1050.00,
        )
        assert stock_tx.get_investment_type() == InvestmentType.STOCK

        # Fund code (common prefix)
        fund_tx = Transaction(
            code="110022",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=2.50,
            total_amount=250.00,
        )
        assert fund_tx.get_investment_type() == InvestmentType.FUND

    def test_total_amount_variance_validation(self):
        """Test total_amount variance validation for fees."""
        # Should allow some variance for fees
        tx = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.00,
            total_amount=1010.00,  # 1% fee
        )
        assert tx.total_amount == 1010.00

        # Large variance is allowed in simplified model
        large_variance_tx = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.00,
            total_amount=1200.00,  # 20% variance
        )
        assert large_variance_tx.total_amount == 1200.00


class TestTransactionList:
    """Test TransactionList model."""

    def test_create_transaction_list(self):
        """Test creating a transaction list."""
        tx1 = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.00,
            total_amount=1000.00,
        )
        tx2 = Transaction(
            code="000002",
            date=date(2023, 2, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=15.00,
            total_amount=750.00,
        )

        tx_list = TransactionList(transactions=[tx1, tx2])
        assert len(tx_list.transactions) == 2
        assert tx1 in tx_list.transactions
        assert tx2 in tx_list.transactions

    def test_filter_by_code(self):
        """Test filtering by investment code."""
        tx1 = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.00,
            total_amount=1000.00,
        )
        tx2 = Transaction(
            code="000002",
            date=date(2023, 2, 15),
            type=TransactionType.BUY,
            quantity=50.0,
            unit_price=20.00,
            total_amount=1000.00,
        )
        tx3 = Transaction(
            code="000001",
            date=date(2023, 3, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=15.00,
            total_amount=750.00,
        )

        tx_list = TransactionList(transactions=[tx1, tx2, tx3])
        filtered = tx_list.filter_by_code("000001")

        assert len(filtered.transactions) == 2
        assert all(tx.code == "000001" for tx in filtered.transactions)

    def test_filter_by_year(self):
        """Test filtering by year."""
        tx1 = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.00,
            total_amount=1000.00,
        )
        tx2 = Transaction(
            code="000001",
            date=date(2022, 12, 15),
            type=TransactionType.BUY,
            quantity=50.0,
            unit_price=8.00,
            total_amount=400.00,
        )
        tx3 = Transaction(
            code="000001",
            date=date(2023, 3, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=15.00,
            total_amount=750.00,
        )

        tx_list = TransactionList(transactions=[tx1, tx2, tx3])
        filtered_2023 = tx_list.filter_by_year(2023)

        assert len(filtered_2023.transactions) == 2
        assert all(tx.date.year == 2023 for tx in filtered_2023.transactions)

    def test_get_codes(self):
        """Test getting unique investment codes."""
        tx1 = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.00,
            total_amount=1000.00,
        )
        tx2 = Transaction(
            code="000002",
            date=date(2023, 2, 15),
            type=TransactionType.BUY,
            quantity=50.0,
            unit_price=20.00,
            total_amount=1000.00,
        )
        tx3 = Transaction(
            code="000001",
            date=date(2023, 3, 15),
            type=TransactionType.SELL,
            quantity=50.0,
            unit_price=15.00,
            total_amount=750.00,
        )

        tx_list = TransactionList(transactions=[tx1, tx2, tx3])
        codes = tx_list.get_codes()

        assert len(codes) == 2
        assert "000001" in codes
        assert "000002" in codes


class TestFifoQueue:
    """Test FifoQueue model."""

    def test_create_fifo_queue(self):
        """Test creating an empty FIFO queue."""
        queue = FifoQueue()
        assert queue.purchases == []
        assert queue.total_quantity == 0
        assert not queue.has_inventory

    def test_add_purchase(self):
        """Test adding purchases to FIFO queue."""
        queue = FifoQueue()
        purchase = Purchase(
            date=date(2023, 1, 15),
            quantity=100.0,
            unit_price=10.00,
            remaining_quantity=100.0,
        )

        queue.add_purchase(purchase)
        assert len(queue.purchases) == 1
        assert queue.total_quantity == 100.0
        assert queue.has_inventory

    def test_get_next_purchase(self):
        """Test getting next purchase from FIFO queue."""
        queue = FifoQueue()
        purchase1 = Purchase(
            date=date(2023, 1, 15),
            quantity=100.0,
            unit_price=10.00,
            remaining_quantity=100.0,
        )
        purchase2 = Purchase(
            date=date(2023, 2, 15),
            quantity=50.0,
            unit_price=12.00,
            remaining_quantity=50.0,
        )

        queue.add_purchase(purchase1)
        queue.add_purchase(purchase2)

        next_purchase = queue.get_next_purchase()
        assert next_purchase == purchase1
        assert next_purchase.remaining_quantity == 100.0

        # Update remaining quantity
        purchase1.remaining_quantity = 0
        next_purchase = queue.get_next_purchase()
        assert next_purchase == purchase2
        assert next_purchase.remaining_quantity == 50.0

    def test_has_inventory(self):
        """Test inventory checking."""
        queue = FifoQueue()
        assert not queue.has_inventory

        purchase = Purchase(
            date=date(2023, 1, 15),
            quantity=100.0,
            unit_price=10.00,
            remaining_quantity=100.0,
        )
        queue.add_purchase(purchase)
        assert queue.has_inventory

        purchase.remaining_quantity = 0
        queue.update_total_quantity()
        assert not queue.has_inventory


class TestValidationResult:
    """Test ValidationResult model."""

    def test_valid_result(self):
        """Test successful validation result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid
        assert result.errors == []
        assert result.warnings == []

    def test_invalid_result(self):
        """Test failed validation result."""
        result = ValidationResult(
            is_valid=False, errors=["Error 1", "Error 2"], warnings=["Warning 1"]
        )
        assert not result.is_valid
        assert result.errors == ["Error 1", "Error 2"]
        assert result.warnings == ["Warning 1"]


class TestHoldingsResult:
    """Test HoldingsResult model."""

    def test_holdings_result(self):
        """Test holdings result model."""
        result = HoldingsResult(
            has_holdings=True,
            quantities={"000001": 100, "000002": 50},
            cost_basis={"000001": 1000.0, "000002": 800.0},
        )
        assert result.has_holdings
        assert result.quantities == {"000001": 100, "000002": 50}
        assert result.cost_basis == {"000001": 1000.0, "000002": 800.0}

    def test_no_holdings(self):
        """Test empty holdings result."""
        result = HoldingsResult(has_holdings=False)
        assert not result.has_holdings
        assert result.quantities == {}
        assert result.cost_basis == {}
