"""Tests for FIFO calculator module."""

import pytest
from datetime import date

from invest_ai.calculation.fifo import FifoCalculator
from invest_ai.models import (
    Transaction,
    TransactionList,
    TransactionType,
    FifoQueue,
    Purchase,
)


class TestFifoCalculatorCoverage:
    """Additional tests for FifoCalculator to boost coverage."""

    def test_init(self):
        """Test initialization."""
        calc = FifoCalculator()
        assert calc is not None

    def test_process_fifo_queue_buy_only(self):
        """Test process_fifo_queue with buy transactions."""
        calc = FifoCalculator()
        transactions = [
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=100,
                unit_price=10.0,
                total_amount=1000,
                transaction_date=date(2023, 1, 15)
            ),
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=50,
                unit_price=12.0,
                total_amount=600,
                transaction_date=date(2023, 2, 15)
            )
        ]
        
        queue = calc.process_fifo_queue(transactions)
        assert queue is not None
        assert queue.get_total_quantity() == 150

    def test_process_fifo_queue_empty_raises(self):
        """Test process_fifo_queue with empty list raises error."""
        calc = FifoCalculator()
        
        with pytest.raises(ValueError, match="empty"):
            calc.process_fifo_queue([])

    def test_process_fifo_queue_mixed_codes_raises(self):
        """Test process_fifo_queue with different codes raises error."""
        calc = FifoCalculator()
        transactions = [
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=100,
                unit_price=10.0,
                total_amount=1000,
                transaction_date=date(2023, 1, 15)
            ),
            Transaction(
                code="000002",  # Different code
                type=TransactionType.BUY,
                quantity=50,
                unit_price=12.0,
                total_amount=600,
                transaction_date=date(2023, 2, 15)
            )
        ]
        
        with pytest.raises(ValueError, match="same code"):
            calc.process_fifo_queue(transactions)

    def test_validate_fifo_processing_valid(self):
        """Test validate_fifo_processing with valid transactions."""
        calc = FifoCalculator()
        transactions = [
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=100,
                unit_price=10.0,
                total_amount=1000,
                transaction_date=date(2023, 1, 15)
            ),
            Transaction(
                code="000001",
                type=TransactionType.SELL,
                quantity=30,
                unit_price=12.0,
                total_amount=360,
                transaction_date=date(2023, 2, 15)
            )
        ]
        
        errors = calc.validate_fifo_processing(transactions)
        assert errors == []

    def test_validate_fifo_processing_oversell(self):
        """Test validate_fifo_processing with overselling."""
        calc = FifoCalculator()
        transactions = [
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=50,
                unit_price=10.0,
                total_amount=500,
                transaction_date=date(2023, 1, 15)
            ),
            Transaction(
                code="000001",
                type=TransactionType.SELL,
                quantity=100,  # More than owned
                unit_price=12.0,
                total_amount=1200,
                transaction_date=date(2023, 2, 15)
            )
        ]
        
        errors = calc.validate_fifo_processing(transactions)
        # Should have error about overselling
        assert len(errors) > 0

    def test_allocate_cost(self):
        """Test allocate_cost method."""
        calc = FifoCalculator()
        
        # First create a queue with purchases
        buy_transactions = [
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=100,
                unit_price=10.0,
                total_amount=1000,
                transaction_date=date(2023, 1, 15)
            )
        ]
        queue = calc.process_fifo_queue(buy_transactions)
        
        # Then allocate cost for a sell
        sell_tx = Transaction(
            code="000001",
            type=TransactionType.SELL,
            quantity=50,
            unit_price=15.0,
            total_amount=750,
            transaction_date=date(2023, 2, 15)
        )
        
        result = calc.allocate_cost(sell_tx, queue)
        assert result is not None
        assert result.cost_basis == 500  # 50 * 10


class TestFifoQueueOperations:
    """Additional tests for FifoQueue operations."""

    def test_multiple_purchases_fifo_order(self):
        """Test that sales use FIFO order."""
        queue = FifoQueue(code="000001")
        
        # Add purchases in different dates
        p1 = Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=100)
        p2 = Purchase(date=date(2023, 2, 1), quantity=100, unit_price=12.0, remaining_quantity=100)
        p3 = Purchase(date=date(2023, 3, 1), quantity=100, unit_price=14.0, remaining_quantity=100)
        
        queue.add_purchase(p1)
        queue.add_purchase(p2)
        queue.add_purchase(p3)
        
        # Sell 150 shares - should use first and part of second purchase
        gains = queue.sell_shares(150, 15.0)
        
        # First 100 from p1 at 10.0, next 50 from p2 at 12.0
        assert len(gains) == 2
        assert gains[0]["quantity"] == 100
        assert gains[0]["gain_loss"] == 500  # (15-10) * 100
        assert gains[1]["quantity"] == 50
        assert gains[1]["gain_loss"] == 150  # (15-12) * 50
