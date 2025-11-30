"""Annual return calculation logic."""

from datetime import date
from typing import Any

from invest_ai.models import (
    AnnualResult,
    CalculationResult,
    PriceData,
    TransactionList,
    TransactionType,
)

from .fifo import FifoCalculator


class AnnualCalculator:
    """Calculates annual investment returns."""

    def __init__(self) -> None:
        """Initialize the annual calculator."""
        self.fifo_calculator = FifoCalculator()

    async def calculate_annual_returns(
        self,
        pre_year_transactions: TransactionList,
        year_transactions: TransactionList,
        year: int,
        code: str | None = None,
        prices: dict[str, dict[str, PriceData]] | None = None,
    ) -> AnnualResult:
        """Calculate annual returns for a specific year.
        
        Args:
            pre_year_transactions: Transactions before the year
            year_transactions: Transactions during the year
            year: The year to calculate returns for
            code: Optional specific investment code
            prices: Dict with 'year_start' and 'year_end' keys, each mapping code to PriceData
        """
        prices = prices or {"year_start": {}, "year_end": {}}
        year_start_prices = prices.get("year_start", {})
        year_end_prices = prices.get("year_end", {})

        # Calculate start value (position at year start using year-start prices)
        start_value_result = await self.calculate_year_start_value(
            pre_year_transactions, year_start_prices
        )

        # Calculate end value (position at year end) and realized gains
        end_value_result = await self.calculate_year_end_performance(
            pre_year_transactions, year_transactions, year_end_prices
        )

        # Calculate new investments during the year
        new_investments = self.calculate_new_investments(year_transactions)
        
        # Calculate withdrawals (sells) during the year
        withdrawals = self.calculate_withdrawals(year_transactions)

        # Calculate annual return rate using Modified Dietz method approximation
        # Net gain = (End Value + Withdrawals) - (Start Value + New Investments)
        start_value = float(start_value_result.get("current_value", 0.0))
        end_value = float(end_value_result.get("current_value", 0.0))
        realized_gains = float(end_value_result.get("realized_gains", 0.0))
        
        net_gain = (end_value + withdrawals + realized_gains) - (start_value + new_investments)

        # Calculate return rate
        # Average capital = start value + weighted average of cash flows
        # Simplified: use (start_value + new_investments) as denominator
        return_rate = 0.0
        denominator = start_value + new_investments
        if denominator > 0:
            return_rate = (net_gain / denominator) * 100

        # Get dividend income
        dividend_income = self.calculate_dividend_income(year_transactions)

        return AnnualResult(
            code=code,
            year=year,
            start_value=start_value,
            end_value=end_value,
            net_gain=net_gain,
            return_rate=return_rate,
            dividends=dividend_income,
            capital_gain=realized_gains,
        )

    async def calculate_year_start_value(
        self,
        pre_year_transactions: TransactionList,
        year_start_prices: dict[str, PriceData],
    ) -> dict[str, Any]:
        """Calculate portfolio value at the start of the year.
        
        Args:
            pre_year_transactions: All transactions before the year
            year_start_prices: Prices at year start for each code
        """
        if not pre_year_transactions.transactions:
            return {"current_value": 0.0, "positions": {}}

        # Calculate positions at year start using FIFO
        codes = pre_year_transactions.get_codes()
        total_value = 0.0
        positions = {}
        
        for code in codes:
            code_transactions = pre_year_transactions.filter_by_code(code).transactions
            
            # Process FIFO to get remaining position
            # Include BUY and DIVIDEND (stock dividends add shares)
            fifo_calculator = FifoCalculator()
            position_transactions = [
                tx for tx in code_transactions 
                if tx.type.name == "BUY" or (tx.type.name == "DIVIDEND" and tx.quantity > 0)
            ]
            if not position_transactions:
                continue
            fifo_queue = fifo_calculator.process_fifo_queue(position_transactions)
            
            # Process sells to update FIFO queue
            for tx in code_transactions:
                if tx.type.name == "SELL":
                    try:
                        result = fifo_calculator.allocate_cost(tx, fifo_queue)
                        fifo_queue = result.remaining_queue
                    except ValueError:
                        continue
            
            # Calculate remaining shares
            remaining_shares = sum(p.remaining_quantity for p in fifo_queue.purchases)
            positions[code] = remaining_shares
            
            # Get price and calculate value
            price_data = year_start_prices.get(code)
            if price_data and remaining_shares > 0:
                total_value += remaining_shares * price_data.price_value
        
        return {"current_value": total_value, "positions": positions}

    def calculate_withdrawals(self, year_transactions: TransactionList) -> float:
        """Calculate total withdrawals (sells) during the year."""
        withdrawals = 0.0
        for transaction in year_transactions.transactions:
            if transaction.type.name == "SELL":
                withdrawals += transaction.total_amount
        return withdrawals

    async def calculate_year_end_performance(
        self,
        pre_year_transactions: TransactionList,
        year_transactions: TransactionList,
        year_end_prices: dict[str, PriceData],
    ) -> dict[str, Any]:
        """Calculate year-end portfolio value and realized gains."""
        # Combine all transactions for the year
        all_transactions = TransactionList(
            transactions=pre_year_transactions.transactions
            + year_transactions.transactions
        )

        # Get unique investment codes
        codes = all_transactions.get_codes()

        individual_results = []
        total_current_value = 0.0
        total_realized_gains = 0.0

        for code in codes:
            # Get transactions for this code
            code_transactions = all_transactions.filter_by_code(code).transactions

            # Calculate FIFO for this code
            # Include BUY and DIVIDEND (stock dividends add shares)
            fifo_calculator = FifoCalculator()
            position_transactions = [
                tx for tx in code_transactions 
                if tx.type.name == "BUY" or (tx.type.name == "DIVIDEND" and tx.quantity > 0)
            ]
            if not position_transactions:
                continue
            fifo_queue = fifo_calculator.process_fifo_queue(position_transactions)

            # Calculate realized gains
            sell_transactions = [
                tx for tx in code_transactions if tx.type.name == "SELL"
            ]
            realized_gains = 0.0

            for sell_tx in sell_transactions:
                try:
                    fifo_result = fifo_calculator.allocate_cost(sell_tx, fifo_queue)
                    realized_gain = fifo_calculator.calculate_realized_gain(
                        sell_tx, fifo_result.cost_basis
                    )
                    realized_gains += realized_gain
                    fifo_queue = fifo_result.remaining_queue
                except ValueError:
                    # Skip invalid sales
                    continue

            # Calculate current value using year-end price
            current_price = year_end_prices.get(code)
            if current_price:
                # Calculate remaining shares from FIFO queue
                remaining_shares = sum(
                    p.remaining_quantity for p in fifo_queue.purchases
                )
                current_value = remaining_shares * current_price.price_value
            else:
                current_value = 0.0

            # Create calculation result
            if code_transactions:
                cost_basis = sum(
                    tx.total_amount
                    for tx in code_transactions
                    if tx.type == TransactionType.BUY
                )
                total_gain = realized_gains + (
                    current_value
                    - sum(
                        p.remaining_quantity * p.unit_price
                        for p in fifo_queue.purchases
                    )
                )
                result = CalculationResult(
                    code=code,
                    investment_type=code_transactions[0].get_investment_type(),
                    realized_gain=realized_gains,
                    unrealized_gain=current_value
                    - sum(
                        p.remaining_quantity * p.unit_price
                        for p in fifo_queue.purchases
                    ),
                    total_gain=total_gain,
                    cost_basis=cost_basis,
                    return_rate=(
                        (total_gain / cost_basis * 100) if cost_basis > 0 else 0.0
                    ),
                    current_value=current_value,
                    total_invested=sum(
                        tx.total_amount
                        for tx in code_transactions
                        if tx.type.name == "BUY"
                    ),
                )
                individual_results.append(result)

            total_current_value += current_value
            total_realized_gains += realized_gains

        return {
            "current_value": total_current_value,
            "realized_gains": total_realized_gains,
            "individual_results": individual_results,
        }

    def calculate_new_investments(self, year_transactions: TransactionList) -> float:
        """Calculate total new investments during the year."""
        new_investments = 0.0

        for transaction in year_transactions.transactions:
            if transaction.type.name == "BUY":
                new_investments += transaction.total_amount

        return new_investments

    def calculate_dividend_income(self, year_transactions: TransactionList) -> float:
        """Calculate dividend income received during the year."""
        dividend_income = 0.0

        for transaction in year_transactions.transactions:
            if transaction.type.name == "DIVIDEND":
                dividend_income += transaction.total_amount

        return dividend_income

    async def calculate_portfolio_annual_returns(
        self,
        pre_year_transactions: TransactionList,
        year_transactions: TransactionList,
        year: int,
        prices: dict[str, dict[str, PriceData]] | None = None,
    ) -> AnnualResult:
        """Calculate annual returns for the entire portfolio."""
        # This is similar to calculate_annual_returns but aggregates across all codes
        return await self.calculate_annual_returns(
            pre_year_transactions, year_transactions, year, code=None, prices=prices
        )


def get_year_start_trading_day(year: int) -> date:
    """Get the first trading day of a year."""
    from ..market.trading_days import get_year_start_trading_day

    return get_year_start_trading_day(year)


def get_year_end_trading_day(year: int) -> date:
    """Get the last trading day of a year."""
    from ..market.trading_days import get_year_end_trading_day

    return get_year_end_trading_day(year)
