"""Tests for reporting modules to boost coverage."""

import pytest
from datetime import date

from invest_ai.models import AnnualResult, HistoryResult, InvestmentType
from invest_ai.reporting.reports import ReportGenerator


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_init(self):
        """Test initialization."""
        generator = ReportGenerator()
        assert generator is not None
        assert generator.console is not None

    @pytest.mark.asyncio
    async def test_format_annual_report(self):
        """Test formatting annual report."""
        generator = ReportGenerator()
        result = AnnualResult(
            year=2023,
            code="000001",
            start_value=10000,
            end_value=12000,
            net_gain=2000,
            return_rate=20.0,
        )
        
        report = await generator.format_annual_report(
            result, investment_type="stock", year=2023, code="000001"
        )
        assert report is not None
        assert len(report) > 0

    @pytest.mark.asyncio
    async def test_format_portfolio_annual_report(self):
        """Test formatting portfolio annual report."""
        generator = ReportGenerator()
        result = AnnualResult(
            year=2023,
            code=None,
            start_value=50000,
            end_value=60000,
            net_gain=10000,
            return_rate=20.0,
        )
        
        report = await generator.format_portfolio_annual_report(
            result, investment_type="stock", year=2023
        )
        assert report is not None

    @pytest.mark.asyncio
    async def test_format_history_report(self):
        """Test formatting history report."""
        generator = ReportGenerator()
        result = HistoryResult(
            investment_type=InvestmentType.STOCK,
            code="000001",
            first_investment=date(2020, 1, 1),
            last_transaction=date(2023, 12, 31),
            total_invested=10000,
            current_value=15000,
            total_gain=5000,
            return_rate=50.0,
        )
        
        report = await generator.format_history_report(
            result, investment_type="stock", code="000001"
        )
        assert report is not None

    @pytest.mark.asyncio
    async def test_format_portfolio_history_report(self):
        """Test formatting portfolio history report."""
        generator = ReportGenerator()
        result = HistoryResult(
            investment_type=InvestmentType.STOCK,
            code=None,
            first_investment=date(2020, 1, 1),
            last_transaction=date(2023, 12, 31),
            total_invested=50000,
            current_value=75000,
            total_gain=25000,
            return_rate=50.0,
        )
        
        report = await generator.format_portfolio_history_report(
            result, investment_type="stock"
        )
        assert report is not None
