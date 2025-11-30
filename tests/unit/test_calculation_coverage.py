"""Additional tests for calculation modules to boost coverage."""

import pytest
from datetime import date

from invest_ai.models import (
    InvestmentType,
    TransactionType,
    Transaction,
    TransactionList,
    PriceData,
    AnnualResult,
    HistoryResult,
)
from invest_ai.calculation.engine import CalculationEngine
from invest_ai.calculation.fifo import FifoCalculator
from invest_ai.calculation.annual import AnnualCalculator
from invest_ai.calculation.history import HistoryCalculator


class TestCalculationEngine:
    """Tests for CalculationEngine class."""

    def test_init(self):
        """Test initialization."""
        engine = CalculationEngine()
        assert engine is not None
        assert engine.annual_calculator is not None
        assert engine.history_calculator is not None

    @pytest.mark.asyncio
    async def test_calculate_annual_returns_empty(self):
        """Test calculate_annual_returns with empty transactions."""
        engine = CalculationEngine()
        pre_year = TransactionList()
        current_year = TransactionList()
        
        result = await engine.calculate_annual_returns(
            pre_year, current_year, 2023, "000001", {}
        )
        assert result is not None
        assert isinstance(result, AnnualResult)

    def test_validate_calculation_inputs_empty(self):
        """Test validate_calculation_inputs with empty transactions."""
        engine = CalculationEngine()
        errors = engine.validate_calculation_inputs(
            TransactionList(), TransactionList(), 2023
        )
        assert "No transactions provided" in errors

    def test_validate_calculation_inputs_invalid_year(self):
        """Test validate_calculation_inputs with invalid year."""
        engine = CalculationEngine()
        tx = Transaction(
            code="000001",
            type=TransactionType.BUY,
            quantity=100,
            total_amount=1000,
            transaction_date=date(2023, 1, 1)
        )
        errors = engine.validate_calculation_inputs(
            TransactionList(transactions=[tx]), TransactionList(), 1980
        )
        assert any("Year" in e for e in errors)

    @pytest.mark.asyncio
    async def test_get_year_end_holdings_empty(self):
        """Test get_year_end_holdings with empty transactions."""
        engine = CalculationEngine()
        result = await engine.get_year_end_holdings(
            TransactionList(), TransactionList(), 2023, "000001"
        )
        assert result is False


class TestFifoCalculator:
    """Tests for FifoCalculator class."""

    def test_init(self):
        """Test initialization."""
        calc = FifoCalculator()
        assert calc is not None

    def test_validate_fifo_processing_empty(self):
        """Test validate_fifo_processing with empty transactions."""
        calc = FifoCalculator()
        errors = calc.validate_fifo_processing([])
        assert errors == []


class TestAnnualCalculator:
    """Tests for AnnualCalculator class."""

    def test_init(self):
        """Test initialization."""
        calc = AnnualCalculator()
        assert calc is not None

    @pytest.mark.asyncio
    async def test_calculate_annual_returns_no_transactions(self):
        """Test annual returns with no transactions."""
        calc = AnnualCalculator()
        
        result = await calc.calculate_annual_returns(
            pre_year_transactions=TransactionList(),
            year_transactions=TransactionList(),
            year=2023,
            prices={},
            code="000001"
        )
        
        assert result is not None
        assert isinstance(result, AnnualResult)
        assert result.year == 2023


class TestHistoryCalculator:
    """Tests for HistoryCalculator class."""

    def test_init(self):
        """Test initialization."""
        calc = HistoryCalculator()
        assert calc is not None

    @pytest.mark.asyncio
    async def test_calculate_history_empty_raises(self):
        """Test calculate_history with empty transactions raises ValueError."""
        calc = HistoryCalculator()
        
        with pytest.raises(ValueError, match="No transactions found"):
            await calc.calculate_single_investment_history(
                transactions=TransactionList(),
                code="000001",
                current_prices={}
            )

    @pytest.mark.asyncio
    async def test_calculate_complete_history_empty_raises(self):
        """Test calculate_complete_history with empty transactions raises ValueError."""
        calc = HistoryCalculator()
        
        with pytest.raises(ValueError, match="No transactions provided"):
            await calc.calculate_complete_history(
                transactions=TransactionList(),
                current_prices={}
            )
