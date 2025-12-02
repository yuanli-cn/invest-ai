"""Complete history calculation logic."""

from datetime import date

from invest_ai.models import (
    CalculationResult,
    HistoryResult,
    PriceData,
    TransactionList,
)

from .fifo import FifoCalculator
from .xirr import build_history_cashflows, calculate_xirr


class HistoryCalculator:
    """Calculates complete investment history."""

    def __init__(self) -> None:
        """Initialize the history calculator."""
        self.fifo_calculator = FifoCalculator()

    async def calculate_complete_history(
        self, transactions: TransactionList, current_prices: dict[str, PriceData]
    ) -> HistoryResult:
        """Calculate complete history for transactions."""
        if not transactions.transactions:
            raise ValueError("No transactions provided")

        # Get investment details
        investment_type = transactions.transactions[0].get_investment_type()
        first_transaction = min(transactions.transactions, key=lambda x: x.date)
        last_transaction = max(transactions.transactions, key=lambda x: x.date)

        # Calculate core metrics
        total_invested = self.calculate_total_invested(transactions)
        current_value = self.calculate_current_value(transactions, current_prices)
        realized_gains, unrealized_gains = self.calculate_gains(
            transactions, current_prices
        )
        dividend_income = self.calculate_dividend_income(transactions)

        total_gain = realized_gains + unrealized_gains
        
        # Calculate return rate using XIRR (professional method)
        tx_cashflows: list[tuple[date, str, float]] = []
        for tx in transactions.transactions:
            if tx.transaction_date:
                tx_cashflows.append((tx.transaction_date, tx.type.name, tx.total_amount))
        
        # Use today or last transaction date as end date
        end_date = last_transaction.date if last_transaction.date else date.today()
        
        xirr_cashflows = build_history_cashflows(
            transactions=tx_cashflows,
            end_date=end_date,
            current_value=current_value,
        )
        return_rate = calculate_xirr(xirr_cashflows)

        # Calculate individual investment results
        individual_results = await self.calculate_individual_results(
            transactions, current_prices
        )

        return HistoryResult(
            investment_type=investment_type,
            code=None,  # For portfolio calculation
            first_investment=first_transaction.date,
            last_transaction=last_transaction.date,
            total_invested=total_invested,
            current_value=current_value,
            total_gain=total_gain,
            return_rate=return_rate,
            realized_gains=realized_gains,
            unrealized_gains=unrealized_gains,
            dividend_income=dividend_income,
            transaction_count=len(transactions.transactions),
            investments=individual_results,
        )

    async def calculate_single_investment_history(
        self,
        transactions: TransactionList,
        code: str,
        current_prices: dict[str, PriceData],
    ) -> HistoryResult:
        """Calculate complete history for a specific investment code."""
        # Filter transactions for the specified code
        code_transactions = transactions.filter_by_code(code)

        if not code_transactions.transactions:
            raise ValueError(f"No transactions found for investment code: {code}")

        # Use the main history calculation
        result = await self.calculate_complete_history(
            code_transactions, current_prices
        )

        # Override the code for single investment calculation
        return HistoryResult(
            investment_type=result.investment_type,
            code=code,  # Set the specific investment code
            first_investment=result.first_investment,
            last_transaction=result.last_transaction,
            total_invested=result.total_invested,
            current_value=result.current_value,
            total_gain=result.total_gain,
            return_rate=result.return_rate,
            realized_gains=result.realized_gains,
            unrealized_gains=result.unrealized_gains,
            dividend_income=result.dividend_income,
            transaction_count=result.transaction_count,
            investments=result.investments,
        )

    async def calculate_portfolio_history(
        self, transactions: TransactionList, current_prices: dict[str, PriceData]
    ) -> HistoryResult:
        """Calculate history for entire portfolio."""
        return await self.calculate_complete_history(transactions, current_prices)

    def calculate_total_invested(self, transactions: TransactionList) -> float:
        """Calculate total amount invested."""
        total = 0.0
        for transaction in transactions.transactions:
            if transaction.type.name == "BUY":
                total += transaction.total_amount
        return total

    def calculate_current_value(
        self, transactions: TransactionList, current_prices: dict[str, PriceData]
    ) -> float:
        """Calculate current market value of holdings."""
        # Get unique investment codes
        codes = transactions.get_codes()
        total_value = 0.0

        for code in codes:
            code_value = self.calculate_code_current_value(
                transactions, code, current_prices
            )
            total_value += code_value

        return total_value

    def calculate_code_current_value(
        self,
        transactions: TransactionList,
        code: str,
        current_prices: dict[str, PriceData],
    ) -> float:
        """Calculate current value for a specific code."""
        # Get transactions for this code
        code_transactions = transactions.filter_by_code(code).transactions

        if not code_transactions:
            return 0.0

        # Process FIFO to get remaining position
        # Include BUY and DIVIDEND (stock dividends add shares)
        position_transactions = [
            tx for tx in code_transactions 
            if tx.type.name == "BUY" or (tx.type.name == "DIVIDEND" and tx.quantity > 0)
        ]
        if not position_transactions:
            return 0.0
        sell_transactions = [tx for tx in code_transactions if tx.type.name == "SELL"]

        fifo_queue = self.fifo_calculator.process_fifo_queue(position_transactions)

        # Process sells to update remaining position
        for sell_tx in sell_transactions:
            try:
                fifo_result = self.fifo_calculator.allocate_cost(sell_tx, fifo_queue)
                fifo_queue = fifo_result.remaining_queue
            except ValueError:
                # Skip invalid sales
                continue

        # Calculate remaining shares
        remaining_shares = sum(p.remaining_quantity for p in fifo_queue.purchases)

        # Get current price
        current_price_data = current_prices.get(code)
        if not current_price_data:
            return 0.0

        return remaining_shares * current_price_data.price_value

    def calculate_gains(
        self, transactions: TransactionList, current_prices: dict[str, PriceData]
    ) -> tuple[float, float]:
        """Calculate realized and unrealized gains."""
        codes = transactions.get_codes()
        total_realized = 0.0
        total_unrealized = 0.0

        for code in codes:
            realized, unrealized = self.calculate_code_gains(
                transactions, code, current_prices
            )
            total_realized += realized
            total_unrealized += unrealized

        return total_realized, total_unrealized

    def calculate_code_gains(
        self,
        transactions: TransactionList,
        code: str,
        current_prices: dict[str, PriceData],
    ) -> tuple[float, float]:
        """Calculate gains for a specific code."""
        code_transactions = transactions.filter_by_code(code).transactions

        if not code_transactions:
            return 0.0, 0.0

        # Process FIFO
        # Include BUY and DIVIDEND (stock dividends add shares)
        position_transactions = [
            tx for tx in code_transactions 
            if tx.type.name == "BUY" or (tx.type.name == "DIVIDEND" and tx.quantity > 0)
        ]
        if not position_transactions:
            return 0.0, 0.0
        sell_transactions = [tx for tx in code_transactions if tx.type.name == "SELL"]

        fifo_queue = self.fifo_calculator.process_fifo_queue(position_transactions)
        realized_gains = 0.0

        # Calculate realized gains from sells
        for sell_tx in sell_transactions:
            try:
                fifo_result = self.fifo_calculator.allocate_cost(sell_tx, fifo_queue)
                realized_gain = self.fifo_calculator.calculate_realized_gain(
                    sell_tx, fifo_result.cost_basis
                )
                realized_gains += realized_gain
                fifo_queue = fifo_result.remaining_queue
            except ValueError:
                continue

        # Calculate unrealized gains from remaining position
        remaining_shares = sum(p.remaining_quantity for p in fifo_queue.purchases)
        remaining_cost_basis = sum(
            p.remaining_quantity * p.unit_price for p in fifo_queue.purchases
        )

        current_price_data = current_prices.get(code)
        if current_price_data:
            current_value = remaining_shares * current_price_data.price_value
            unrealized_gains = current_value - remaining_cost_basis
        else:
            unrealized_gains = 0.0

        return realized_gains, unrealized_gains

    def calculate_dividend_income(self, transactions: TransactionList) -> float:
        """Calculate total dividend income."""
        dividend_income = 0.0
        for transaction in transactions.transactions:
            if transaction.type.name == "DIVIDEND":
                dividend_income += transaction.total_amount

        return dividend_income

    async def calculate_individual_results(
        self, transactions: TransactionList, current_prices: dict[str, PriceData]
    ) -> list[CalculationResult]:
        """Calculate results for individual investments."""
        codes = transactions.get_codes()
        individual_results = []

        for code in codes:
            code_result = await self.calculate_code_result(
                transactions, code, current_prices
            )
            individual_results.append(code_result)

        return individual_results

    async def calculate_code_result(
        self,
        transactions: TransactionList,
        code: str,
        current_prices: dict[str, PriceData],
    ) -> CalculationResult:
        """Calculate result for a specific code."""
        code_transactions = transactions.filter_by_code(code).transactions

        if not code_transactions:
            raise ValueError(f"No transactions found for code: {code}")

        investment_type = code_transactions[0].get_investment_type()
        total_invested = sum(
            tx.total_amount for tx in code_transactions if tx.type.name == "BUY"
        )

        realized, unrealized = self.calculate_code_gains(
            transactions, code, current_prices
        )
        total_gain = realized + unrealized
        
        current_value = self.calculate_code_current_value(
            transactions, code, current_prices
        )
        
        # Calculate return rate using XIRR (professional method)
        tx_cashflows: list[tuple[date, str, float]] = []
        for tx in code_transactions:
            if tx.transaction_date:
                tx_cashflows.append((tx.transaction_date, tx.type.name, tx.total_amount))
        
        # Find last transaction date for this code
        last_tx = max(code_transactions, key=lambda x: x.date) if code_transactions else None
        end_date = last_tx.date if last_tx and last_tx.date else date.today()
        
        xirr_cashflows = build_history_cashflows(
            transactions=tx_cashflows,
            end_date=end_date,
            current_value=current_value,
        )
        return_rate = calculate_xirr(xirr_cashflows)

        return CalculationResult(
            code=code,
            investment_type=investment_type,
            realized_gain=realized,
            unrealized_gain=unrealized,
            total_gain=total_gain,
            return_rate=return_rate,
            cost_basis=total_invested,
            current_value=current_value,
            total_invested=total_invested,
        )
