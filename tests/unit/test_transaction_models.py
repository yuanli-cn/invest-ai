"""Tests for transaction models to boost coverage."""

import pytest
from datetime import date

from invest_ai.models import Transaction, TransactionList, TransactionType
from invest_ai.transaction.models import TransactionSummary, PortfolioSnapshot


class TestTransactionSummary:
    """Tests for TransactionSummary class."""

    def test_empty_transactions(self):
        """Test summary with empty transactions."""
        tx_list = TransactionList()
        summary = TransactionSummary(tx_list)
        
        assert summary.total_transactions == 0
        assert summary.total_buy_value == 0.0
        assert summary.total_sell_value == 0.0
        assert summary.total_dividend_income == 0.0
        assert summary.date_range is None

    def test_with_transactions(self):
        """Test summary with various transactions."""
        tx_list = TransactionList(transactions=[
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                total_amount=1000,
                transaction_date=date(2023, 1, 1)
            ),
            Transaction(
                code="000001",
                type=TransactionType.SELL,
                total_amount=500,
                transaction_date=date(2023, 6, 1)
            ),
            Transaction(
                code="000001",
                type=TransactionType.DIVIDEND,
                total_amount=50,
                transaction_date=date(2023, 3, 1)
            ),
        ])
        summary = TransactionSummary(tx_list)
        
        assert summary.total_transactions == 3
        assert summary.total_buy_value == 1000
        assert summary.total_sell_value == 500
        assert summary.total_dividend_income == 50
        assert summary.unique_codes == {"000001"}

    def test_net_cash_flow(self):
        """Test net_cash_flow property."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500),
            Transaction(code="000001", type=TransactionType.DIVIDEND, total_amount=50),
        ])
        summary = TransactionSummary(tx_list)
        
        # -1000 + 500 + 50 = -450
        assert summary.net_cash_flow == -450

    def test_date_properties(self):
        """Test first and last transaction date properties."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000, transaction_date=date(2023, 1, 1)),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500, transaction_date=date(2023, 12, 31)),
        ])
        summary = TransactionSummary(tx_list)
        
        assert summary.first_transaction_date == date(2023, 1, 1)
        assert summary.last_transaction_date == date(2023, 12, 31)

    def test_date_properties_empty(self):
        """Test date properties with no dates."""
        tx_list = TransactionList()
        summary = TransactionSummary(tx_list)
        
        assert summary.first_transaction_date is None
        assert summary.last_transaction_date is None

    def test_get_code_count(self):
        """Test get_code_count method."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500),
        ])
        summary = TransactionSummary(tx_list)
        
        assert summary.get_code_count() == 2


class TestPortfolioSnapshot:
    """Tests for PortfolioSnapshot class."""

    def test_init(self):
        """Test initialization."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        assert snapshot.target_date == date(2023, 12, 31)
        assert snapshot.positions == {}
        assert snapshot.cost_basis == {}
        assert snapshot.transactions == []

    def test_add_buy_transaction(self):
        """Test adding buy transaction."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        tx = Transaction(
            code="000001",
            type=TransactionType.BUY,
            quantity=100,
            total_amount=1000,
            transaction_date=date(2023, 1, 1)
        )
        snapshot.add_transaction(tx)
        
        assert snapshot.positions["000001"] == 100
        assert snapshot.cost_basis["000001"] == 1000

    def test_add_sell_transaction(self):
        """Test adding sell transaction."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        
        # First buy
        buy_tx = Transaction(
            code="000001",
            type=TransactionType.BUY,
            quantity=100,
            total_amount=1000
        )
        snapshot.add_transaction(buy_tx)
        
        # Then sell
        sell_tx = Transaction(
            code="000001",
            type=TransactionType.SELL,
            quantity=30,
            total_amount=400
        )
        snapshot.add_transaction(sell_tx)
        
        assert snapshot.positions["000001"] == 70

    def test_add_stock_dividend(self):
        """Test adding stock dividend transaction."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        
        # First buy
        buy_tx = Transaction(
            code="000001",
            type=TransactionType.BUY,
            quantity=100,
            total_amount=1000
        )
        snapshot.add_transaction(buy_tx)
        
        # Stock dividend
        div_tx = Transaction(
            code="000001",
            type=TransactionType.DIVIDEND,
            quantity=10,  # Stock dividend adds shares
            total_amount=0
        )
        snapshot.add_transaction(div_tx)
        
        assert snapshot.positions["000001"] == 110

    def test_get_position(self):
        """Test get_position method."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        snapshot.positions["000001"] = 100
        
        assert snapshot.get_position("000001") == 100
        assert snapshot.get_position("000002") == 0

    def test_get_positions(self):
        """Test get_positions method."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        snapshot.positions = {"000001": 100, "000002": 0, "000003": 50}
        
        positions = snapshot.get_positions()
        assert positions == {"000001": 100, "000003": 50}

    def test_has_position(self):
        """Test has_position method."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        snapshot.positions["000001"] = 100
        snapshot.positions["000002"] = 0
        
        assert snapshot.has_position("000001") is True
        assert snapshot.has_position("000002") is False
        assert snapshot.has_position("000003") is False

    def test_get_total_positions_value(self):
        """Test get_total_positions_value method."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        snapshot.positions = {"000001": 100, "000002": 50}
        
        prices = {"000001": 10.0, "000002": 20.0}
        total = snapshot.get_total_positions_value(prices)
        
        # 100 * 10 + 50 * 20 = 1000 + 1000 = 2000
        assert total == 2000.0

    def test_get_cost_basis(self):
        """Test get_cost_basis method."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        snapshot.cost_basis["000001"] = 1000
        
        assert snapshot.get_cost_basis("000001") == 1000
        assert snapshot.get_cost_basis("000002") == 0.0

    def test_get_total_cost_basis(self):
        """Test get_total_cost_basis method."""
        snapshot = PortfolioSnapshot(date(2023, 12, 31))
        snapshot.cost_basis = {"000001": 1000, "000002": 500}
        
        assert snapshot.get_total_cost_basis() == 1500
