"""Core data models for Invest AI."""

from datetime import date
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

# =============================================================================
# Enums
# =============================================================================


class InvestmentType(str, Enum):
    """Type of investment (stock or fund)."""

    STOCK = "stock"
    FUND = "fund"


class TransactionType(str, Enum):
    """Type of transaction."""

    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"


# =============================================================================
# Core Data Models
# =============================================================================


class PriceData(BaseModel):
    """Stock price data point."""

    code: str
    price_date: date
    price_value: float
    source: str = "unknown"

    def __str__(self) -> str:
        return f"{self.code} @ {self.price_date}: ¥{self.price_value:.2f}"


class NavData(BaseModel):
    """Fund Net Asset Value (NAV) data."""

    code: str
    nav_date: date
    nav: float
    accumulated_nav: float | None = Field(default=None)

    def to_price_data(self) -> PriceData:
        """Convert NAV data to PriceData format."""
        return PriceData(
            code=self.code, price_date=self.nav_date, price_value=self.nav, source="nav"
        )


class Transaction(BaseModel):
    """Individual investment transaction."""

    code: str
    transaction_date: date | None = Field(default=None, alias="date")
    type: TransactionType
    quantity: float = 0.0
    unit_price: float = 0.0
    total_amount: float
    dividend_type: str | None = Field(default=None)
    amount_per_share: float | None = Field(default=None)
    name: str | None = Field(default=None)
    notes: str | None = Field(default=None)

    model_config = {"populate_by_name": True}

    def is_buy(self) -> bool:
        """Check if this is a buy transaction."""
        return self.type == TransactionType.BUY

    def is_sell(self) -> bool:
        """Check if this is a sell transaction."""
        return self.type == TransactionType.SELL

    def is_dividend(self) -> bool:
        """Check if this is a dividend transaction."""
        return self.type == TransactionType.DIVIDEND

    def is_cash_dividend(self) -> bool:
        """Check if this is a cash dividend."""
        return self.is_dividend() and self.dividend_type == "cash"

    def get_investment_type(self) -> InvestmentType:
        """Get the investment type based on transaction characteristics."""
        return (
            InvestmentType.FUND
            if self.code.startswith(("5", "1"))
            else InvestmentType.STOCK
        )

    @property
    def date(self) -> date | None:
        """Alias for transaction_date."""
        return self.transaction_date

    @date.setter
    def date(self, value: Union["date", None]) -> None:
        """Setter for transaction_date."""
        self.transaction_date = value


class TransactionList(BaseModel):
    """Container for multiple transactions."""

    transactions: list[Transaction] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.transactions)

    def __iter__(self):
        return iter(self.transactions)

    def append(self, transaction: Transaction) -> None:
        """Add a transaction."""
        self.transactions.append(transaction)

    def extend(self, transactions: list[Transaction]) -> None:
        """Add multiple transactions."""
        self.transactions.extend(transactions)

    def sort_by_date(self) -> None:
        """Sort transactions by date."""
        self.transactions.sort(
            key=lambda x: x.transaction_date if x.transaction_date else date.min
        )

    def get_codes(self) -> set[str]:
        """Get all unique investment codes."""
        return {tx.code for tx in self.transactions}

    def get_date_range(self) -> tuple[date | None, date | None]:
        """Get earliest and latest transaction dates."""
        dates = [tx.transaction_date for tx in self.transactions if tx.transaction_date]
        if not dates:
            return None, None
        return min(dates), max(dates)

    def filter_by_code(self, code: str) -> "TransactionList":
        """Filter transactions by investment code."""
        filtered = [tx for tx in self.transactions if tx.code == code]
        return TransactionList(transactions=filtered)

    def filter_by_year(self, year: int) -> "TransactionList":
        """Filter transactions by year."""
        filtered = [
            tx
            for tx in self.transactions
            if tx.transaction_date and tx.transaction_date.year == year
        ]
        result = TransactionList(transactions=filtered)
        return result

    def add_transaction(self, transaction: "Transaction") -> None:
        """Add a transaction to the list."""
        self.transactions.append(transaction)


# =============================================================================
# Filtering and Validation
# =============================================================================


class FilterCriteria(BaseModel):
    """Criteria for filtering transactions."""

    investment_type: InvestmentType | None = Field(default=None)
    code: str | None = Field(default=None)
    year: int | None = Field(default=None)
    before_year: int | None = Field(default=None)
    after_date: date | None = Field(default=None)
    before_date: date | None = Field(default=None)
    date_range: tuple[date | None, date | None] | None = Field(default=None)


class ValidationResult(BaseModel):
    """Result of transaction validation."""

    is_valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# =============================================================================
# Calculation Results
# =============================================================================


class AnnualResult(BaseModel):
    """Annual return calculation result."""

    year: int
    code: str | None = Field(default=None)
    start_value: float = 0.0
    end_value: float = 0.0
    net_gain: float = 0.0
    return_rate: float = 0.0
    dividends: float = 0.0
    capital_gain: float = 0.0


class HistoryResult(BaseModel):
    """Complete investment history result."""

    code: str | None = Field(default=None)
    investment_type: str | None = Field(default=None)
    total_invested: float = 0.0
    current_value: float = 0.0
    total_gain: float = 0.0
    return_rate: float = 0.0
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    dividend_income: float = 0.0
    realized_gains: float = 0.0
    unrealized_gains: float = 0.0
    first_investment: date | None = Field(default=None)
    last_transaction: date | None = Field(default=None)
    transaction_count: int = 0
    investments: list[Any] = Field(default_factory=list)


class CalculationResult(BaseModel):
    """Individual investment calculation result."""

    code: str
    investment_type: InvestmentType
    realized_gain: float
    unrealized_gain: float | None = None
    total_gain: float
    cost_basis: float
    return_rate: float
    current_value: float
    total_invested: float


# =============================================================================
# FIFO Calculation Models
# =============================================================================


class Purchase(BaseModel):
    """Individual purchase for FIFO calculation."""

    date: date
    quantity: float
    unit_price: float
    remaining_quantity: float = 0.0

    @property
    def total_cost(self) -> float:
        """Calculate total cost of purchase."""
        return self.quantity * self.unit_price

    def remaining_cost(self) -> float:
        """Calculate remaining cost basis."""
        return self.remaining_quantity * self.unit_price


class FifoResult(BaseModel):
    """Result of FIFO cost basis calculation."""

    code: str
    allocated_purchases: list[Purchase] = Field(default_factory=list)
    cost_basis: float = 0.0
    remaining_queue: Optional["FifoQueue"] = Field(default=None)
    realized_gains: list[dict[str, Any]] = Field(default_factory=list)


class FifoQueue(BaseModel):
    """FIFO queue for tracking purchases."""

    code: str = Field(default="000000")
    purchases: list[Purchase] = Field(default_factory=list)

    def add_purchase(self, purchase: Purchase) -> None:
        """Add a purchase to the queue."""
        self.purchases.append(purchase)
        self.purchases.sort(key=lambda x: x.date)

    def sell_shares(
        self, sell_quantity: float, sell_price: float
    ) -> list[dict[str, Any]]:
        """Execute a sell using FIFO method."""
        realized_gains = []
        remaining_to_sell = sell_quantity

        while remaining_to_sell > 0 and self.purchases:
            purchase = self.purchases[0]
            available = purchase.remaining_quantity

            if available <= remaining_to_sell:
                sell_quantity_from_this = available
                self.purchases.pop(0)
            else:
                sell_quantity_from_this = remaining_to_sell
                purchase.remaining_quantity -= remaining_to_sell
                remaining_to_sell = 0

            cost = sell_quantity_from_this * purchase.unit_price
            proceeds = sell_quantity_from_this * sell_price
            gain_loss = proceeds - cost

            realized_gains.append(
                {
                    "quantity": sell_quantity_from_this,
                    "sell_price": sell_price,
                    "cost_basis": cost,
                    "proceeds": proceeds,
                    "gain_loss": gain_loss,
                    "purchase_date": purchase.date,
                }
            )

            remaining_to_sell -= sell_quantity_from_this

        if remaining_to_sell > 0:
            raise ValueError(
                f"Cannot sell {sell_quantity} shares of {self.code}, only {sell_quantity - remaining_to_sell} available"
            )

        return realized_gains

    def get_total_quantity(self) -> float:
        """Get total remaining shares."""
        return sum(p.remaining_quantity for p in self.purchases)

    def get_total_cost_basis(self) -> float:
        """Get total cost basis."""
        return sum(p.remaining_cost() for p in self.purchases)

    def get_average_cost(self) -> float:
        """Get average cost per share."""
        total_qty = self.get_total_quantity()
        if total_qty == 0:
            return 0.0
        return self.get_total_cost_basis() / total_qty

    def update_total_quantity(self) -> None:
        """Update total quantity by removing purchases with zero remaining quantity."""
        self.purchases = [p for p in self.purchases if p.remaining_quantity > 0]

    @property
    def total_quantity(self) -> float:
        """Get total remaining shares (property version)."""
        return self.get_total_quantity()

    def get_next_purchase(self) -> Purchase | None:
        """Get the next purchase to sell (FIFO)."""
        for p in self.purchases:
            if p.remaining_quantity > 0:
                return p
        return None

    @property
    def has_inventory(self) -> bool:
        """Check if there are any remaining shares."""
        return any(p.remaining_quantity > 0 for p in self.purchases)


# =============================================================================
# API Response Models
# =============================================================================


class PriceResponse(BaseModel):
    """Response from price fetching API."""

    data: dict[str, list[PriceData]] = Field(default_factory=dict)
    errors: dict[str, str] = Field(default_factory=dict)
    cached: bool = False


class HoldingsResult(BaseModel):
    """Result of holdings calculation."""

    has_holdings: bool = False
    quantities: dict[str, float] = Field(default_factory=dict)
    cost_basis: dict[str, float] = Field(default_factory=dict)

    def get_quantity(self, code: str) -> float:
        """Get quantity for a specific code."""
        return self.quantities.get(code, 0.0)

    def get_cost_basis(self, code: str) -> float:
        """Get cost basis for a specific code."""
        return self.cost_basis.get(code, 0.0)
