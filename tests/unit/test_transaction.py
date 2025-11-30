"""Tests for transaction processing (loader, validator, filter)."""

from datetime import date

import pytest

from invest_ai.models import (
    FilterCriteria,
    Transaction,
    TransactionList,
    TransactionType,
)
from invest_ai.transaction import (
    TransactionFilter,
    TransactionLoader,
    TransactionValidator,
)


class TestTransactionLoader:
    """Test transaction loading functionality."""

    @pytest.mark.asyncio
    async def test_load_yaml_file(self, sample_yaml_file):
        """Test loading transactions from YAML file."""
        loader = TransactionLoader()
        transactions = await loader.load_transactions(str(sample_yaml_file))

        assert isinstance(transactions, TransactionList)
        assert len(transactions.transactions) == 3
        assert transactions.transactions[0].code == "000001"
        assert transactions.transactions[0].type == TransactionType.BUY

    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        loader = TransactionLoader()
        with pytest.raises(FileNotFoundError):
            await loader.load_transactions("nonexistent.yaml")

    @pytest.mark.asyncio
    async def test_empty_yaml_file(self, tmp_path):
        """Test loading empty YAML file."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")

        loader = TransactionLoader()
        transactions = await loader.load_transactions(str(empty_file))

        assert isinstance(transactions, TransactionList)
        assert len(transactions.transactions) == 0

    @pytest.mark.asyncio
    async def test_invalid_yaml_file(self, tmp_path):
        """Test loading invalid YAML file."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content: [")

        loader = TransactionLoader()
        with pytest.raises(ValueError, match="Invalid YAML format"):
            await loader.load_transactions(str(invalid_file))


class TestTransactionValidator:
    """Test transaction validation."""

    @pytest.mark.asyncio
    async def test_validate_valid_transactions(self):
        """Test validation of valid transactions."""
        from invest_ai.models import Transaction

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
                quantity=0.0,
                unit_price=0.00,
                total_amount=500.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 6, 15),
                type=TransactionType.SELL,
                quantity=50.0,
                unit_price=15.00,
                total_amount=750.00,
            ),
        ]

        validator = TransactionValidator()
        result = await validator.validate_transactions(
            TransactionList(transactions=transactions)
        )

        assert result.is_valid
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_future_date_transaction(self):
        """Test validation of future date transaction."""
        future_date = date.today().replace(year=date.today().year + 1)
        transaction = Transaction(
            code="000001",
            date=future_date,
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=10.00,
            total_amount=1000.00,
        )

        validator = TransactionValidator()
        result = await validator.validate_single_transaction(transaction)

        assert result.is_valid
        # Should have warning about future date
        assert any("future" in warning.lower() for warning in result.warnings)

    @pytest.mark.asyncio
    async def test_validate_zero_quantity_buy(self):
        """Test validation of zero quantity buy transaction."""
        transaction = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=0.0,
            unit_price=10.00,
            total_amount=0.00,
        )

        validator = TransactionValidator()
        result = await validator.validate_single_transaction(transaction)

        assert not result.is_valid
        assert any("Buy quantity must be positive" in error for error in result.errors)

    @pytest.mark.asyncio
    async def test_validate_zero_unit_price(self):
        """Test validation of zero unit price transaction."""
        transaction = Transaction(
            code="000001",
            date=date(2023, 1, 15),
            type=TransactionType.BUY,
            quantity=100.0,
            unit_price=0.0,
            total_amount=1000.00,
        )

        validator = TransactionValidator()
        result = await validator.validate_single_transaction(transaction)

        assert not result.is_valid
        assert any(
            "Buy unit price must be positive" in error for error in result.errors
        )

    @pytest.mark.asyncio
    async def test_validate_missing_dividend_fields(self):
        """Test validation of dividend without proper field combination."""
        transaction = Transaction(
            code="000001",
            date=date(2023, 3, 15),
            type=TransactionType.DIVIDEND,
            quantity=0.0,
            unit_price=0.0,
            total_amount=500.00,
        )

        validator = TransactionValidator()
        result = await validator.validate_single_transaction(transaction)

        # Validation now based on data context, not dividend_type field
        # Cash dividend: quantity=0, total_amount>0 should be valid
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_transaction_consistency(self):
        """Test validation of transaction consistency."""
        # Valid: more buys than sells
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
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=12.00,
                total_amount=600.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 3, 15),
                type=TransactionType.SELL,
                quantity=75.0,
                unit_price=15.00,
                total_amount=1125.00,
            ),
        ]

        validator = TransactionValidator()
        result = await validator.validate_transactions(
            TransactionList(transactions=valid_transactions)
        )

        assert result.is_valid

        # Invalid: sells more than bought
        invalid_transactions = [
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
                quantity=150.0,
                unit_price=15.00,
                total_amount=2250.00,
            ),
        ]

        result = await validator.validate_transactions(
            TransactionList(transactions=invalid_transactions)
        )
        assert not result.is_valid
        assert "Negative position" in result.errors[0]


class TestTransactionFilter:
    """Test transaction filtering functionality."""

    def setup_transactions(self):
        """Setup sample transactions for testing."""
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
                code="000002",
                date=date(2023, 1, 16),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=20.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2022, 12, 15),
                type=TransactionType.BUY,
                quantity=50.0,
                unit_price=8.00,
                total_amount=400.00,
            ),
            Transaction(
                code="000002",
                date=date(2023, 2, 15),
                type=TransactionType.SELL,
                quantity=25.0,
                unit_price=25.00,
                total_amount=625.00,
            ),
            Transaction(
                code="000003",
                date=date(2023, 3, 15),
                type=TransactionType.BUY,
                quantity=200.0,
                unit_price=5.00,
                total_amount=1000.00,
            ),
            Transaction(
                code="000001",
                date=date(2023, 4, 15),
                type=TransactionType.SELL,
                quantity=75.0,
                unit_price=12.00,
                total_amount=900.00,
            ),
        ]

    @pytest.mark.asyncio
    async def test_filter_by_code(self):
        """Test filtering by investment code."""
        transactions = self.setup_transactions()
        tx_list = TransactionList(transactions=transactions)
        filter_obj = TransactionFilter()

        result = await filter_obj.filter_transactions(
            tx_list, FilterCriteria(code="000001")
        )

        assert len(result.transactions) == 3
        assert all(tx.code == "000001" for tx in result.transactions)

    @pytest.mark.asyncio
    async def test_filter_by_year(self):
        """Test filtering by year."""
        transactions = self.setup_transactions()
        tx_list = TransactionList(transactions=transactions)
        filter_obj = TransactionFilter()

        result_2023 = await filter_obj.filter_transactions(
            tx_list, FilterCriteria(year=2023)
        )
        result_2022 = await filter_obj.filter_transactions(
            tx_list, FilterCriteria(year=2022)
        )

        assert len(result_2023.transactions) == 5
        assert all(tx.date.year == 2023 for tx in result_2023.transactions)
        assert len(result_2022.transactions) == 1
        assert result_2022.transactions[0].date.year == 2022

    @pytest.mark.asyncio
    async def test_filter_before_year(self):
        """Test filtering before a specific year."""
        transactions = self.setup_transactions()
        tx_list = TransactionList(transactions=transactions)
        filter_obj = TransactionFilter()

        result = await filter_obj.filter_transactions(
            tx_list, FilterCriteria(before_year=2023)
        )

        assert len(result.transactions) == 1
        assert result.transactions[0].date.year == 2022

    @pytest.mark.asyncio
    async def test_get_transactions_by_code(self):
        """Test grouping transactions by code."""
        transactions = self.setup_transactions()
        tx_list = TransactionList(transactions=transactions)
        filter_obj = TransactionFilter()

        code_groups = await filter_obj.get_transactions_by_code(tx_list)

        assert len(code_groups) == 3
        assert "000001" in code_groups
        assert "000002" in code_groups
        assert "000003" in code_groups
        assert len(code_groups["000001"].transactions) == 3

    @pytest.mark.asyncio
    async def test_get_buy_transactions(self):
        """Test filtering for buy transactions."""
        transactions = self.setup_transactions()
        tx_list = TransactionList(transactions=transactions)
        filter_obj = TransactionFilter()

        buy_transactions = await filter_obj.get_buy_transactions(tx_list)

        assert len(buy_transactions.transactions) == 4
        assert all(
            tx.type == TransactionType.BUY for tx in buy_transactions.transactions
        )

    @pytest.mark.asyncio
    async def test_get_sell_transactions(self):
        """Test filtering for sell transactions."""
        transactions = self.setup_transactions()
        tx_list = TransactionList(transactions=transactions)
        filter_obj = TransactionFilter()

        sell_transactions = await filter_obj.get_sell_transactions(tx_list)

        assert len(sell_transactions.transactions) == 2
        assert all(
            tx.type == TransactionType.SELL for tx in sell_transactions.transactions
        )

    @pytest.mark.asyncio
    async def test_date_range_filtering(self):
        """Test filtering by date range."""
        transactions = self.setup_transactions()
        tx_list = TransactionList(transactions=transactions)
        filter_obj = TransactionFilter()

        start_date = date(2023, 1, 1)
        end_date = date(2023, 2, 28)

        result = await filter_obj.filter_transactions(
            tx_list, FilterCriteria(date_range=(start_date, end_date))
        )

        assert len(result.transactions) == 3
        assert all(start_date <= tx.date <= end_date for tx in result.transactions)
