"""Tests for model classes to boost coverage."""

import pytest
from datetime import date

from invest_ai.models import (
    InvestmentType,
    TransactionType,
    PriceData,
    NavData,
    Transaction,
    TransactionList,
    FilterCriteria,
    ValidationResult,
    AnnualResult,
    HistoryResult,
    CalculationResult,
    Purchase,
    FifoResult,
    FifoQueue,
    PriceResponse,
    HoldingsResult,
)


class TestPriceData:
    """Tests for PriceData model."""

    def test_str_representation(self):
        """Test string representation."""
        price = PriceData(
            code="000001",
            price_date=date(2023, 1, 15),
            price_value=10.50,
            source="tushare"
        )
        result = str(price)
        assert "000001" in result
        assert "10.50" in result


class TestNavData:
    """Tests for NavData model."""

    def test_to_price_data(self):
        """Test conversion to PriceData."""
        nav = NavData(
            code="110022",
            nav_date=date(2023, 1, 15),
            nav=1.5678,
            accumulated_nav=2.0
        )
        price = nav.to_price_data()
        assert price.code == "110022"
        assert price.price_date == date(2023, 1, 15)
        assert price.price_value == 1.5678
        assert price.source == "nav"


class TestTransaction:
    """Tests for Transaction model."""

    def test_is_buy(self):
        """Test is_buy method."""
        tx = Transaction(code="000001", type=TransactionType.BUY, total_amount=1000)
        assert tx.is_buy() is True
        assert tx.is_sell() is False
        assert tx.is_dividend() is False

    def test_is_sell(self):
        """Test is_sell method."""
        tx = Transaction(code="000001", type=TransactionType.SELL, total_amount=1000)
        assert tx.is_sell() is True
        assert tx.is_buy() is False

    def test_is_dividend(self):
        """Test is_dividend method."""
        tx = Transaction(code="000001", type=TransactionType.DIVIDEND, total_amount=100)
        assert tx.is_dividend() is True

    def test_is_cash_dividend(self):
        """Test is_cash_dividend method."""
        tx = Transaction(
            code="000001",
            type=TransactionType.DIVIDEND,
            total_amount=100,
            dividend_type="cash"
        )
        assert tx.is_cash_dividend() is True

        tx2 = Transaction(
            code="000001",
            type=TransactionType.DIVIDEND,
            total_amount=100,
            dividend_type="stock"
        )
        assert tx2.is_cash_dividend() is False

    def test_get_investment_type_stock(self):
        """Test get_investment_type for stock."""
        tx = Transaction(code="000001", type=TransactionType.BUY, total_amount=1000)
        assert tx.get_investment_type() == InvestmentType.STOCK

        tx2 = Transaction(code="300001", type=TransactionType.BUY, total_amount=1000)
        assert tx2.get_investment_type() == InvestmentType.STOCK

        tx3 = Transaction(code="600001", type=TransactionType.BUY, total_amount=1000)
        assert tx3.get_investment_type() == InvestmentType.STOCK

    def test_get_investment_type_fund(self):
        """Test get_investment_type for fund."""
        tx = Transaction(code="510050", type=TransactionType.BUY, total_amount=1000)
        assert tx.get_investment_type() == InvestmentType.FUND

        tx2 = Transaction(code="110022", type=TransactionType.BUY, total_amount=1000)
        assert tx2.get_investment_type() == InvestmentType.FUND

    def test_date_property(self):
        """Test date property getter and setter."""
        tx = Transaction(code="000001", type=TransactionType.BUY, total_amount=1000)
        tx.date = date(2023, 1, 15)
        assert tx.date == date(2023, 1, 15)
        assert tx.transaction_date == date(2023, 1, 15)


class TestTransactionList:
    """Tests for TransactionList model."""

    def test_len(self):
        """Test __len__ method."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000),
        ])
        assert len(tx_list) == 2

    def test_iter(self):
        """Test __iter__ method."""
        tx1 = Transaction(code="000001", type=TransactionType.BUY, total_amount=1000)
        tx2 = Transaction(code="000002", type=TransactionType.BUY, total_amount=2000)
        tx_list = TransactionList(transactions=[tx1, tx2])
        
        result = list(tx_list)
        assert len(result) == 2
        assert result[0] == tx1

    def test_append(self):
        """Test append method."""
        tx_list = TransactionList()
        tx = Transaction(code="000001", type=TransactionType.BUY, total_amount=1000)
        tx_list.append(tx)
        assert len(tx_list) == 1

    def test_extend(self):
        """Test extend method."""
        tx_list = TransactionList()
        txs = [
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000),
        ]
        tx_list.extend(txs)
        assert len(tx_list) == 2

    def test_sort_by_date(self):
        """Test sort_by_date method."""
        tx1 = Transaction(code="000001", type=TransactionType.BUY, total_amount=1000, transaction_date=date(2023, 3, 1))
        tx2 = Transaction(code="000002", type=TransactionType.BUY, total_amount=2000, transaction_date=date(2023, 1, 1))
        tx3 = Transaction(code="000003", type=TransactionType.BUY, total_amount=3000, transaction_date=date(2023, 2, 1))
        tx_list = TransactionList(transactions=[tx1, tx2, tx3])
        
        tx_list.sort_by_date()
        assert tx_list.transactions[0].code == "000002"
        assert tx_list.transactions[1].code == "000003"
        assert tx_list.transactions[2].code == "000001"

    def test_get_codes(self):
        """Test get_codes method."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500),
        ])
        codes = tx_list.get_codes()
        assert codes == {"000001", "000002"}

    def test_get_date_range(self):
        """Test get_date_range method."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000, transaction_date=date(2023, 3, 1)),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000, transaction_date=date(2023, 1, 1)),
        ])
        start, end = tx_list.get_date_range()
        assert start == date(2023, 1, 1)
        assert end == date(2023, 3, 1)

    def test_get_date_range_empty(self):
        """Test get_date_range with no dates."""
        tx_list = TransactionList()
        start, end = tx_list.get_date_range()
        assert start is None
        assert end is None

    def test_filter_by_code(self):
        """Test filter_by_code method."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500),
        ])
        filtered = tx_list.filter_by_code("000001")
        assert len(filtered) == 2

    def test_filter_by_year(self):
        """Test filter_by_year method."""
        tx_list = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000, transaction_date=date(2023, 1, 1)),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000, transaction_date=date(2022, 1, 1)),
        ])
        filtered = tx_list.filter_by_year(2023)
        assert len(filtered) == 1
        assert filtered.transactions[0].code == "000001"

    def test_add_transaction(self):
        """Test add_transaction method."""
        tx_list = TransactionList()
        tx = Transaction(code="000001", type=TransactionType.BUY, total_amount=1000)
        tx_list.add_transaction(tx)
        assert len(tx_list) == 1


class TestPurchase:
    """Tests for Purchase model."""

    def test_total_cost(self):
        """Test total_cost property."""
        purchase = Purchase(
            date=date(2023, 1, 1),
            quantity=100,
            unit_price=10.0,
            remaining_quantity=100
        )
        assert purchase.total_cost == 1000.0

    def test_remaining_cost(self):
        """Test remaining_cost method."""
        purchase = Purchase(
            date=date(2023, 1, 1),
            quantity=100,
            unit_price=10.0,
            remaining_quantity=50
        )
        assert purchase.remaining_cost() == 500.0


class TestFifoQueue:
    """Tests for FifoQueue model."""

    def test_add_purchase(self):
        """Test add_purchase method."""
        queue = FifoQueue(code="000001")
        p1 = Purchase(date=date(2023, 2, 1), quantity=100, unit_price=10.0, remaining_quantity=100)
        p2 = Purchase(date=date(2023, 1, 1), quantity=50, unit_price=9.0, remaining_quantity=50)
        
        queue.add_purchase(p1)
        queue.add_purchase(p2)
        
        # Should be sorted by date
        assert queue.purchases[0].date == date(2023, 1, 1)
        assert queue.purchases[1].date == date(2023, 2, 1)

    def test_get_total_quantity(self):
        """Test get_total_quantity method."""
        queue = FifoQueue(code="000001")
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=100),
            Purchase(date=date(2023, 2, 1), quantity=50, unit_price=11.0, remaining_quantity=50),
        ]
        assert queue.get_total_quantity() == 150

    def test_get_total_cost_basis(self):
        """Test get_total_cost_basis method."""
        queue = FifoQueue(code="000001")
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=100),
            Purchase(date=date(2023, 2, 1), quantity=50, unit_price=12.0, remaining_quantity=50),
        ]
        # 100 * 10 + 50 * 12 = 1000 + 600 = 1600
        assert queue.get_total_cost_basis() == 1600.0

    def test_get_average_cost(self):
        """Test get_average_cost method."""
        queue = FifoQueue(code="000001")
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=100),
            Purchase(date=date(2023, 2, 1), quantity=50, unit_price=12.0, remaining_quantity=50),
        ]
        # 1600 / 150 = 10.67
        assert abs(queue.get_average_cost() - 10.666666666666666) < 0.01

    def test_get_average_cost_empty(self):
        """Test get_average_cost with empty queue."""
        queue = FifoQueue(code="000001")
        assert queue.get_average_cost() == 0.0

    def test_sell_shares(self):
        """Test sell_shares method."""
        queue = FifoQueue(code="000001")
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=100),
            Purchase(date=date(2023, 2, 1), quantity=50, unit_price=12.0, remaining_quantity=50),
        ]
        
        gains = queue.sell_shares(120, 15.0)
        
        # Should sell all 100 from first purchase, 20 from second
        assert len(gains) == 2
        assert gains[0]["quantity"] == 100
        assert gains[0]["gain_loss"] == 500  # (15 - 10) * 100
        assert gains[1]["quantity"] == 20
        assert gains[1]["gain_loss"] == 60  # (15 - 12) * 20

    def test_sell_shares_insufficient(self):
        """Test sell_shares with insufficient inventory."""
        queue = FifoQueue(code="000001")
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=50),
        ]
        
        with pytest.raises(ValueError, match="Cannot sell"):
            queue.sell_shares(100, 15.0)

    def test_total_quantity_property(self):
        """Test total_quantity property."""
        queue = FifoQueue(code="000001")
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=100),
        ]
        assert queue.total_quantity == 100

    def test_get_next_purchase(self):
        """Test get_next_purchase method."""
        queue = FifoQueue(code="000001")
        p1 = Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=0)
        p2 = Purchase(date=date(2023, 2, 1), quantity=50, unit_price=12.0, remaining_quantity=50)
        queue.purchases = [p1, p2]
        
        next_p = queue.get_next_purchase()
        assert next_p == p2

    def test_get_next_purchase_empty(self):
        """Test get_next_purchase with empty queue."""
        queue = FifoQueue(code="000001")
        assert queue.get_next_purchase() is None

    def test_has_inventory(self):
        """Test has_inventory property."""
        queue = FifoQueue(code="000001")
        assert queue.has_inventory is False
        
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=50),
        ]
        assert queue.has_inventory is True

    def test_update_total_quantity(self):
        """Test update_total_quantity method."""
        queue = FifoQueue(code="000001")
        queue.purchases = [
            Purchase(date=date(2023, 1, 1), quantity=100, unit_price=10.0, remaining_quantity=0),
            Purchase(date=date(2023, 2, 1), quantity=50, unit_price=12.0, remaining_quantity=50),
        ]
        
        queue.update_total_quantity()
        assert len(queue.purchases) == 1
        assert queue.purchases[0].remaining_quantity == 50


class TestHoldingsResult:
    """Tests for HoldingsResult model."""

    def test_get_quantity(self):
        """Test get_quantity method."""
        holdings = HoldingsResult(
            has_holdings=True,
            quantities={"000001": 100, "000002": 200}
        )
        assert holdings.get_quantity("000001") == 100
        assert holdings.get_quantity("000003") == 0.0

    def test_get_cost_basis(self):
        """Test get_cost_basis method."""
        holdings = HoldingsResult(
            has_holdings=True,
            cost_basis={"000001": 1000, "000002": 2000}
        )
        assert holdings.get_cost_basis("000001") == 1000
        assert holdings.get_cost_basis("000003") == 0.0
