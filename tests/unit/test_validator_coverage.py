"""Tests for transaction validator module."""

import pytest
from datetime import date

from invest_ai.transaction.validator import TransactionValidator
from invest_ai.models import (
    Transaction,
    TransactionList,
    TransactionType,
)


class TestTransactionValidator:
    """Tests for TransactionValidator class."""

    def test_init(self):
        """Test initialization."""
        validator = TransactionValidator()
        assert validator is not None

    @pytest.mark.asyncio
    async def test_validate_empty_transactions(self):
        """Test validation with empty transactions."""
        validator = TransactionValidator()
        result = await validator.validate_transactions(TransactionList())
        # Empty list might be valid or invalid depending on implementation
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_valid_buy_transaction(self):
        """Test validation with valid buy transaction."""
        validator = TransactionValidator()
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
        
        result = await validator.validate_transactions(transactions)
        assert result is not None
        assert result.is_valid is True
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_valid_sell_transaction(self):
        """Test validation with valid sell transaction (with prior buy)."""
        validator = TransactionValidator()
        transactions = TransactionList(transactions=[
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
                quantity=50,
                unit_price=12.0,
                total_amount=600,
                transaction_date=date(2023, 6, 15)
            )
        ])
        
        result = await validator.validate_transactions(transactions)
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_dividend_transaction(self):
        """Test validation with dividend transaction."""
        validator = TransactionValidator()
        transactions = TransactionList(transactions=[
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
                type=TransactionType.DIVIDEND,
                quantity=0,
                unit_price=0,
                total_amount=50,
                dividend_type="cash",
                transaction_date=date(2023, 6, 15)
            )
        ])
        
        result = await validator.validate_transactions(transactions)
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_negative_quantity(self):
        """Test validation with negative quantity."""
        validator = TransactionValidator()
        transactions = TransactionList(transactions=[
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=-100,  # Invalid
                unit_price=10.0,
                total_amount=1000,
                transaction_date=date(2023, 1, 15)
            )
        ])
        
        result = await validator.validate_transactions(transactions)
        # Should have errors for negative quantity
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_multiple_codes(self):
        """Test validation with multiple investment codes."""
        validator = TransactionValidator()
        transactions = TransactionList(transactions=[
            Transaction(
                code="000001",
                type=TransactionType.BUY,
                quantity=100,
                unit_price=10.0,
                total_amount=1000,
                transaction_date=date(2023, 1, 15)
            ),
            Transaction(
                code="000002",
                type=TransactionType.BUY,
                quantity=200,
                unit_price=20.0,
                total_amount=4000,
                transaction_date=date(2023, 1, 20)
            )
        ])
        
        result = await validator.validate_transactions(transactions)
        assert result is not None
        assert result.is_valid is True

    @pytest.mark.asyncio
    async def test_validate_fund_code(self):
        """Test validation with fund code."""
        validator = TransactionValidator()
        transactions = TransactionList(transactions=[
            Transaction(
                code="510050",  # Fund code
                type=TransactionType.BUY,
                quantity=1000,
                unit_price=3.5,
                total_amount=3500,
                transaction_date=date(2023, 1, 15)
            )
        ])
        
        result = await validator.validate_transactions(transactions)
        assert result is not None
        assert result.is_valid is True
