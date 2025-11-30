"""Transaction-specific models and utilities."""

from datetime import date

from invest_ai.models import Transaction, TransactionList, TransactionType


class TransactionSummary:
    """Summary statistics for a transaction list."""

    def __init__(self, transactions: TransactionList):
        """Initialize the summary."""
        self.transactions = transactions
        self._calculate_stats()

    def _calculate_stats(self) -> None:
        """Calculate summary statistics."""
        if not self.transactions.transactions:
            self.total_transactions = 0
            self.total_buy_value = 0.0
            self.total_sell_value = 0.0
            self.total_dividend_income = 0.0
            self.unique_codes: set[str] = set()
            self.date_range = None
            return

        self.total_transactions = len(self.transactions.transactions)
        self.total_buy_value = 0.0
        self.total_sell_value = 0.0
        self.total_dividend_income = 0.0
        self.unique_codes: set[str] = set()

        dates = []

        for tx in self.transactions.transactions:
            self.unique_codes.add(tx.code)

            if tx.date:
                dates.append(tx.date)

            if tx.type == TransactionType.BUY:
                self.total_buy_value += tx.total_amount
            elif tx.type == TransactionType.SELL:
                self.total_sell_value += tx.total_amount
            elif tx.type == TransactionType.DIVIDEND:
                self.total_dividend_income += tx.total_amount

        # Calculate date range
        if dates:
            dates.sort()
            self.date_range = (dates[0], dates[-1])
        else:
            self.date_range = None

    @property
    def net_cash_flow(self) -> float:
        """Calculate net cash flow (buys - sells + dividends)."""
        return (
            -self.total_buy_value + self.total_sell_value + self.total_dividend_income
        )

    @property
    def first_transaction_date(self) -> date | None:
        """Get the date of the first transaction."""
        return self.date_range[0] if self.date_range else None

    @property
    def last_transaction_date(self) -> date | None:
        """Get the date of the last transaction."""
        return self.date_range[1] if self.date_range else None

    def get_code_count(self) -> int:
        """Get the number of unique investment codes."""
        return len(self.unique_codes)


class PortfolioSnapshot:
    """Portfolio snapshot at a specific point in time."""

    def __init__(self, target_date: date):
        """Initialize the portfolio snapshot."""
        self.target_date = target_date
        self.positions: dict[str, float] = {}  # code -> quantity
        self.cost_basis: dict[str, float] = {}  # code -> total cost
        self.transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the snapshot."""
        self.transactions.append(transaction)

        code = transaction.code

        if transaction.type == TransactionType.BUY:
            self.positions[code] = self.positions.get(code, 0) + transaction.quantity
            self.cost_basis[code] = (
                self.cost_basis.get(code, 0) + transaction.total_amount
            )

        elif transaction.type == TransactionType.SELL:
            self.positions[code] = self.positions.get(code, 0) - transaction.quantity
            # Cost basis is calculated per share, remaining cost basis will be handled by FIFO

        elif transaction.type == TransactionType.DIVIDEND:
            # Stock dividends increase position without affecting cost basis
            if transaction.quantity > 0:
                self.positions[code] = (
                    self.positions.get(code, 0) + transaction.quantity
                )

    def get_position(self, code: str) -> float:
        """Get the position quantity for a specific code."""
        return self.positions.get(code, 0)

    def get_positions(self) -> dict[str, float]:
        """Get all positions."""
        return {code: qty for code, qty in self.positions.items() if qty > 0}

    def has_position(self, code: str) -> bool:
        """Check if there's a position for a specific code."""
        return self.get_position(code) > 0

    def get_total_positions_value(self, prices: dict[str, float]) -> float:
        """Calculate total value of all positions using provided prices."""
        total = 0.0
        for code, quantity in self.get_positions().items():
            price = prices.get(code, 0.0)
            total += quantity * price
        return total

    def get_cost_basis(self, code: str) -> float:
        """Get the cost basis for a specific code."""
        return self.cost_basis.get(code, 0.0)

    def get_total_cost_basis(self) -> float:
        """Get total cost basis for all positions."""
        return sum(self.cost_basis.values())
