"""Main calculation engine orchestrating all calculations."""

from invest_ai.models import (
    AnnualResult,
    HistoryResult,
    PriceData,
    TransactionList,
)

from .annual import AnnualCalculator
from .history import HistoryCalculator


class CalculationEngine:
    """Main calculation engine for investment P&L calculations."""

    def __init__(self) -> None:
        """Initialize the calculation engine."""
        self.annual_calculator = AnnualCalculator()
        self.history_calculator = HistoryCalculator()

    async def calculate_annual_returns(
        self,
        pre_year_transactions: TransactionList,
        year_transactions: TransactionList,
        year: int,
        code: str | None = None,
        prices: dict[str, dict[str, PriceData]] | None = None,
    ) -> AnnualResult:
        """Calculate annual returns for specific year.
        
        Args:
            pre_year_transactions: Transactions before the year
            year_transactions: Transactions during the year
            year: The year to calculate
            code: Optional specific investment code
            prices: Dict with 'year_start' and 'year_end' keys for price data
        """
        return await self.annual_calculator.calculate_annual_returns(
            pre_year_transactions, year_transactions, year, code, prices
        )

    async def calculate_portfolio_annual_returns(
        self,
        pre_year_transactions: TransactionList,
        year_transactions: TransactionList,
        year: int,
        prices: dict[str, dict[str, PriceData]] | None = None,
    ) -> AnnualResult:
        """Calculate portfolio annual returns."""
        return await self.calculate_annual_returns(
            pre_year_transactions, year_transactions, year, code=None, prices=prices
        )

    async def calculate_complete_history(
        self, transactions: TransactionList, current_prices: dict[str, PriceData]
    ) -> HistoryResult:
        """Calculate complete investment history."""
        return await self.history_calculator.calculate_complete_history(
            transactions, current_prices
        )

    async def calculate_single_investment_history(
        self, transactions: TransactionList, code: str, current_prices: dict[str, PriceData]
    ) -> HistoryResult:
        """Calculate complete investment history for a specific code."""
        return await self.history_calculator.calculate_single_investment_history(
            transactions, code, current_prices
        )

    async def calculate_portfolio_history(
        self, transactions: TransactionList, current_prices: dict[str, PriceData] | None = None
    ) -> HistoryResult:
        """Calculate portfolio history (will need current prices)."""
        return await self.calculate_complete_history(
            transactions, current_prices or {}
        )

    async def get_year_end_holdings(
        self,
        pre_year_transactions: TransactionList,
        year_transactions: TransactionList,
        year: int,
        code: str | None = None,
    ) -> bool:
        """Get holdings at year end for validation."""
        # This would implement the holdings checking logic from our sequence diagrams
        # For now, return a simple placeholder
        all_transactions = TransactionList(
            transactions=pre_year_transactions.transactions
            + year_transactions.transactions
        )

        if code:
            all_transactions = all_transactions.filter_by_code(code)

        if not all_transactions.transactions:
            return False

        return True  # Placeholder - would implement actual logic

    def validate_calculation_inputs(
        self,
        pre_year_transactions: TransactionList,
        year_transactions: TransactionList,
        year: int,
    ) -> list[str]:
        """Validate inputs for annual calculation."""
        errors = []

        if (
            not pre_year_transactions.transactions
            and not year_transactions.transactions
        ):
            errors.append("No transactions provided")

        if year < 1990 or year > 2030:
            errors.append("Year outside valid range (1990-2030)")

        # Validate transaction consistency
        all_transactions = TransactionList(
            transactions=pre_year_transactions.transactions
            + year_transactions.transactions
        )

        # Check for negative positions
        fifo_calculator = self.annual_calculator.fifo_calculator
        validation_errors = fifo_calculator.validate_fifo_processing(
            all_transactions.transactions
        )
        errors.extend(validation_errors)

        return errors
