"""Unit tests for XIRR calculation."""

from datetime import date

import pytest

from invest_ai.calculation.xirr import (
    build_annual_cashflows,
    build_history_cashflows,
    calculate_xirr,
)


class TestCalculateXIRR:
    """Tests for the calculate_xirr function."""

    def test_simple_investment_positive_return(self) -> None:
        """Test XIRR with simple investment and positive return."""
        # Invest 10000, get back 11000 after 1 year = 10% return
        cashflows = [
            (date(2024, 1, 1), -10000),
            (date(2025, 1, 1), 11000),
        ]
        result = calculate_xirr(cashflows)
        assert 9.5 < result < 10.5  # Allow for small calculation variance

    def test_simple_investment_negative_return(self) -> None:
        """Test XIRR with simple investment and negative return."""
        # Invest 10000, get back 9000 after 1 year = -10% return
        cashflows = [
            (date(2024, 1, 1), -10000),
            (date(2025, 1, 1), 9000),
        ]
        result = calculate_xirr(cashflows)
        assert -10.5 < result < -9.5

    def test_multiple_investments(self) -> None:
        """Test XIRR with multiple investments during the year."""
        # Initial investment + mid-year additional investment
        cashflows = [
            (date(2024, 1, 1), -10000),
            (date(2024, 7, 1), -5000),
            (date(2025, 1, 1), 16500),  # Final value
        ]
        result = calculate_xirr(cashflows)
        # Should be around 10-12% considering timing
        assert 8.0 < result < 15.0

    def test_investment_with_dividends(self) -> None:
        """Test XIRR including dividend cash flows."""
        cashflows = [
            (date(2024, 1, 1), -10000),
            (date(2024, 6, 15), 200),  # Dividend
            (date(2024, 12, 31), 10500),  # Final value
        ]
        result = calculate_xirr(cashflows)
        assert 6.0 < result < 8.0

    def test_investment_with_partial_sale(self) -> None:
        """Test XIRR with partial sale during the period."""
        cashflows = [
            (date(2024, 1, 1), -10000),
            (date(2024, 6, 1), 3000),  # Partial sale
            (date(2024, 12, 31), 8000),  # Remaining value
        ]
        result = calculate_xirr(cashflows)
        assert 8.0 < result < 15.0

    def test_empty_cashflows(self) -> None:
        """Test XIRR with empty cash flows returns 0."""
        result = calculate_xirr([])
        assert result == 0.0

    def test_single_cashflow(self) -> None:
        """Test XIRR with single cash flow returns 0."""
        cashflows = [(date(2024, 1, 1), -10000)]
        result = calculate_xirr(cashflows)
        assert result == 0.0

    def test_all_positive_cashflows(self) -> None:
        """Test XIRR with all positive cash flows returns 0."""
        cashflows = [
            (date(2024, 1, 1), 10000),
            (date(2024, 12, 31), 11000),
        ]
        result = calculate_xirr(cashflows)
        assert result == 0.0

    def test_all_negative_cashflows(self) -> None:
        """Test XIRR with all negative cash flows returns 0."""
        cashflows = [
            (date(2024, 1, 1), -10000),
            (date(2024, 12, 31), -5000),
        ]
        result = calculate_xirr(cashflows)
        assert result == 0.0

    def test_zero_cashflows_filtered(self) -> None:
        """Test that zero cash flows are filtered out."""
        cashflows = [
            (date(2024, 1, 1), -10000),
            (date(2024, 6, 1), 0),  # Zero cash flow
            (date(2024, 12, 31), 11000),
        ]
        result = calculate_xirr(cashflows)
        assert 9.5 < result < 10.5


class TestBuildAnnualCashflows:
    """Tests for build_annual_cashflows function."""

    def test_basic_annual_cashflows(self) -> None:
        """Test building basic annual cash flows."""
        transactions = [
            (date(2024, 3, 15), "BUY", 5000),
            (date(2024, 6, 20), "SELL", 2000),
            (date(2024, 9, 10), "DIVIDEND", 100),
        ]
        result = build_annual_cashflows(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            start_value=10000,
            end_value=12000,
            transactions=transactions,
        )

        # Should have: start value, buy, sell, dividend, end value
        assert len(result) == 5
        # Start value (negative)
        assert result[0] == (date(2024, 1, 1), -10000)
        # Buy (negative)
        assert (date(2024, 3, 15), -5000) in result
        # Sell (positive)
        assert (date(2024, 6, 20), 2000) in result
        # Dividend (positive)
        assert (date(2024, 9, 10), 100) in result
        # End value (positive)
        assert result[-1] == (date(2024, 12, 31), 12000)

    def test_no_transactions(self) -> None:
        """Test annual cash flows with no transactions."""
        result = build_annual_cashflows(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            start_value=10000,
            end_value=11000,
            transactions=[],
        )

        assert len(result) == 2
        assert result[0] == (date(2024, 1, 1), -10000)
        assert result[1] == (date(2024, 12, 31), 11000)

    def test_zero_start_value(self) -> None:
        """Test annual cash flows with zero start value."""
        transactions = [
            (date(2024, 3, 15), "BUY", 5000),
        ]
        result = build_annual_cashflows(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            start_value=0,
            end_value=5500,
            transactions=transactions,
        )

        # No start value cash flow
        assert len(result) == 2
        assert (date(2024, 3, 15), -5000) in result
        assert (date(2024, 12, 31), 5500) in result


class TestBuildHistoryCashflows:
    """Tests for build_history_cashflows function."""

    def test_basic_history_cashflows(self) -> None:
        """Test building basic history cash flows."""
        transactions = [
            (date(2023, 1, 15), "BUY", 10000),
            (date(2023, 6, 20), "DIVIDEND", 200),
            (date(2024, 3, 10), "BUY", 5000),
        ]
        result = build_history_cashflows(
            transactions=transactions,
            end_date=date(2024, 12, 31),
            current_value=18000,
        )

        assert len(result) == 4
        assert (date(2023, 1, 15), -10000) in result
        assert (date(2023, 6, 20), 200) in result
        assert (date(2024, 3, 10), -5000) in result
        assert result[-1] == (date(2024, 12, 31), 18000)

    def test_history_with_sales(self) -> None:
        """Test history cash flows including sales."""
        transactions = [
            (date(2023, 1, 15), "BUY", 10000),
            (date(2023, 8, 1), "SELL", 4000),
        ]
        result = build_history_cashflows(
            transactions=transactions,
            end_date=date(2024, 12, 31),
            current_value=8000,
        )

        assert len(result) == 3
        assert (date(2023, 1, 15), -10000) in result
        assert (date(2023, 8, 1), 4000) in result
        assert (date(2024, 12, 31), 8000) in result

    def test_zero_current_value(self) -> None:
        """Test history cash flows with zero current value (all sold)."""
        transactions = [
            (date(2023, 1, 15), "BUY", 10000),
            (date(2024, 6, 1), "SELL", 12000),
        ]
        result = build_history_cashflows(
            transactions=transactions,
            end_date=date(2024, 12, 31),
            current_value=0,
        )

        # No current value cash flow
        assert len(result) == 2
        assert (date(2023, 1, 15), -10000) in result
        assert (date(2024, 6, 1), 12000) in result
