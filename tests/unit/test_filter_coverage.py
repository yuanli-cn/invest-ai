"""Tests for transaction filter module."""

import pytest
from datetime import date

from invest_ai.transaction.filter import TransactionFilter
from invest_ai.models import (
    Transaction,
    TransactionList,
    TransactionType,
    InvestmentType,
    FilterCriteria,
)


class TestTransactionFilter:
    """Tests for TransactionFilter class."""

    def test_init(self):
        """Test initialization."""
        filter_obj = TransactionFilter()
        assert filter_obj is not None

    @pytest.mark.asyncio
    async def test_filter_by_code(self):
        """Test filtering by code."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500),
        ])
        
        criteria = FilterCriteria(code="000001")
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 2

    @pytest.mark.asyncio
    async def test_filter_by_year(self):
        """Test filtering by year."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000, transaction_date=date(2023, 1, 15)),
            Transaction(code="000001", type=TransactionType.BUY, total_amount=2000, transaction_date=date(2022, 6, 1)),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500, transaction_date=date(2023, 12, 1)),
        ])
        
        criteria = FilterCriteria(year=2023)
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 2

    @pytest.mark.asyncio
    async def test_filter_by_investment_type_stock(self):
        """Test filtering by investment type (stock)."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),  # Stock
            Transaction(code="510050", type=TransactionType.BUY, total_amount=2000),  # Fund
        ])
        
        criteria = FilterCriteria(investment_type=InvestmentType.STOCK)
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 1
        assert result.transactions[0].code == "000001"

    @pytest.mark.asyncio
    async def test_filter_by_investment_type_fund(self):
        """Test filtering by investment type (fund)."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),  # Stock
            Transaction(code="510050", type=TransactionType.BUY, total_amount=2000),  # Fund
        ])
        
        criteria = FilterCriteria(investment_type=InvestmentType.FUND)
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 1
        assert result.transactions[0].code == "510050"

    @pytest.mark.asyncio
    async def test_filter_before_year(self):
        """Test filtering before a specific year."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000, transaction_date=date(2021, 1, 15)),
            Transaction(code="000001", type=TransactionType.BUY, total_amount=2000, transaction_date=date(2022, 6, 1)),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500, transaction_date=date(2023, 12, 1)),
        ])
        
        criteria = FilterCriteria(before_year=2023)
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 2

    @pytest.mark.asyncio
    async def test_filter_combined_criteria(self):
        """Test filtering with multiple criteria."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000, transaction_date=date(2023, 1, 15)),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000, transaction_date=date(2023, 6, 1)),
            Transaction(code="000001", type=TransactionType.SELL, total_amount=500, transaction_date=date(2022, 12, 1)),
        ])
        
        criteria = FilterCriteria(code="000001", year=2023)
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 1

    @pytest.mark.asyncio
    async def test_filter_empty_transactions(self):
        """Test filtering empty transaction list."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList()
        criteria = FilterCriteria(code="000001")
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 0

    @pytest.mark.asyncio
    async def test_filter_no_criteria(self):
        """Test filtering with no criteria returns all."""
        filter_obj = TransactionFilter()
        
        transactions = TransactionList(transactions=[
            Transaction(code="000001", type=TransactionType.BUY, total_amount=1000),
            Transaction(code="000002", type=TransactionType.BUY, total_amount=2000),
        ])
        
        criteria = FilterCriteria()
        result = await filter_obj.filter_transactions(transactions, criteria)
        
        assert len(result.transactions) == 2
