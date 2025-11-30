"""Transaction filtering functionality."""

from datetime import date

from invest_ai.models import (
    FilterCriteria,
    InvestmentType,
    Transaction,
    TransactionList,
    TransactionType,
)


class TransactionFilter:
    """Filters transactions based on various criteria."""

    def __init__(self) -> None:
        """Initialize the transaction filter."""

    async def filter_transactions(
        self, transactions: TransactionList, criteria: FilterCriteria
    ) -> TransactionList:
        """Filter transactions based on the provided criteria."""
        filtered_transactions = transactions.transactions.copy()

        # Apply filters in order
        if criteria.investment_type:
            filtered_transactions = self._filter_by_investment_type(
                filtered_transactions, criteria.investment_type
            )

        if criteria.code:
            filtered_transactions = self._filter_by_code(
                filtered_transactions, criteria.code
            )

        if criteria.year:
            filtered_transactions = self._filter_by_year(
                filtered_transactions, criteria.year
            )

        if criteria.before_year:
            filtered_transactions = self._filter_before_year(
                filtered_transactions, criteria.before_year
            )

        if criteria.date_range:
            start_date, end_date = criteria.date_range
            filtered_transactions = self._filter_by_date_range(
                filtered_transactions, start_date, end_date
            )

        return TransactionList(transactions=filtered_transactions)

    def _filter_by_investment_type(
        self, transactions: list[Transaction], investment_type: InvestmentType
    ) -> list[Transaction]:
        """Filter transactions by investment type."""
        return [
            tx for tx in transactions if tx.get_investment_type() == investment_type
        ]

    def _filter_by_code(
        self, transactions: list[Transaction], code: str
    ) -> list[Transaction]:
        """Filter transactions by investment code."""
        # Normalize code (ensure 6-digit format)
        normalized_code = code.zfill(6)
        return [tx for tx in transactions if tx.code == normalized_code]

    def _filter_by_year(
        self, transactions: list[Transaction], year: int
    ) -> list[Transaction]:
        """Filter transactions by year."""
        return [tx for tx in transactions if tx.date.year == year]

    def _filter_before_year(
        self, transactions: list[Transaction], year: int
    ) -> list[Transaction]:
        """Filter transactions before a specific year."""
        return [tx for tx in transactions if tx.date.year < year]

    def _filter_by_date_range(
        self, transactions: list[Transaction], start_date: date, end_date: date
    ) -> list[Transaction]:
        """Filter transactions by date range (inclusive)."""
        return [tx for tx in transactions if start_date <= tx.date <= end_date]

    def _filter_by_transaction_type(
        self, transactions: list[Transaction], transaction_type: TransactionType
    ) -> list[Transaction]:
        """Filter transactions by transaction type."""
        return [tx for tx in transactions if tx.type == transaction_type]

    async def get_transactions_by_year(
        self, transactions: TransactionList, year: int
    ) -> dict[int, TransactionList]:
        """Group transactions by year."""
        yearly_transactions = {}

        for transaction in transactions.transactions:
            year_key = transaction.date.year
            if year_key not in yearly_transactions:
                yearly_transactions[year_key] = TransactionList()
            yearly_transactions[year_key].add_transaction(transaction)

        return yearly_transactions

    async def get_transactions_by_code(
        self, transactions: TransactionList
    ) -> dict[str, TransactionList]:
        """Group transactions by investment code."""
        code_transactions = {}

        for transaction in transactions.transactions:
            if transaction.code not in code_transactions:
                code_transactions[transaction.code] = TransactionList()
            code_transactions[transaction.code].add_transaction(transaction)

        return code_transactions

    async def get_buy_transactions(
        self, transactions: TransactionList
    ) -> TransactionList:
        """Get only buy transactions."""
        buy_transactions = self._filter_by_transaction_type(
            transactions.transactions, TransactionType.BUY
        )
        return TransactionList(transactions=buy_transactions)

    async def get_sell_transactions(
        self, transactions: TransactionList
    ) -> TransactionList:
        """Get only sell transactions."""
        sell_transactions = self._filter_by_transaction_type(
            transactions.transactions, TransactionType.SELL
        )
        return TransactionList(transactions=sell_transactions)

    async def get_dividend_transactions(
        self, transactions: TransactionList
    ) -> TransactionList:
        """Get only dividend transactions."""
        dividend_transactions = self._filter_by_transaction_type(
            transactions.transactions, TransactionType.DIVIDEND
        )
        return TransactionList(transactions=dividend_transactions)

    async def get_transactions_in_date_range(
        self, transactions: TransactionList, start_year: int, end_year: int
    ) -> TransactionList:
        """Get transactions within a year range."""
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)

        filtered = self._filter_by_date_range(
            transactions.transactions, start_date, end_date
        )
        return TransactionList(transactions=filtered)

    async def get_pre_year_transactions(
        self, transactions: TransactionList, year: int
    ) -> TransactionList:
        """Get all transactions before a specific year."""
        pre_year_transactions = self._filter_before_year(
            transactions.transactions, year
        )
        return TransactionList(transactions=pre_year_transactions)

    async def get_transactions_for_calculation(
        self,
        transactions: TransactionList,
        investment_type: InvestmentType,
        code: str | None = None,
        year: int | None = None,
        before_year: int | None = None,
    ) -> dict[str, TransactionList]:
        """Get transactions organized for calculation scenarios."""

        # Create base filter criteria
        base_criteria = FilterCriteria(investment_type=investment_type)

        # Apply code filter if specified
        if code:
            base_criteria.code = code

        # Filter base transactions
        filtered_base = await self.filter_transactions(transactions, base_criteria)

        result = {"all": filtered_base}

        # Add year-specific filters if requested
        if year:
            year_criteria = FilterCriteria(
                investment_type=investment_type, code=code, year=year
            )
            result["year"] = await self.filter_transactions(transactions, year_criteria)

        # Add pre-year transactions if requested
        if before_year:
            pre_year_criteria = FilterCriteria(
                investment_type=investment_type, code=code, before_year=before_year
            )
            result["pre_year"] = await self.filter_transactions(
                transactions, pre_year_criteria
            )

        return result
