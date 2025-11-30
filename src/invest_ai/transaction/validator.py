"""Transaction validation logic."""

from datetime import datetime

from invest_ai.models import (
    Transaction,
    TransactionList,
    TransactionType,
    ValidationResult,
)


class TransactionValidator:
    """Validates transaction data for consistency and correctness."""

    def __init__(self) -> None:
        """Initialize the validator."""

    async def validate_transactions(
        self, transactions: TransactionList
    ) -> ValidationResult:
        """Validate a list of transactions."""
        errors = []
        warnings = []

        if not transactions.transactions:
            return ValidationResult(is_valid=False, errors=["No transactions found"])

        # Validate each transaction
        for i, transaction in enumerate(transactions.transactions):
            result = await self.validate_single_transaction(transaction, i)
            errors.extend(result.errors)
            warnings.extend(result.warnings)

        # Validate consistency across transactions
        consistency_result = await self.validate_transaction_consistency(transactions)
        errors.extend(consistency_result.errors)
        warnings.extend(consistency_result.warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    async def validate_single_transaction(
        self, transaction: Transaction, index: int = 0
    ) -> ValidationResult:
        """Validate a single transaction."""
        errors = []
        warnings = []

        try:
            # Validate code format
            if not transaction.code.isdigit():
                # Allow alphabetic codes for international stocks
                if not transaction.code.isalpha():
                    errors.append(
                        f"Transaction {index + 1}: Code must be numeric or alphabetic"
                    )
                else:
                    warnings.append(
                        f"Transaction {index + 1}: International stock code detected"
                    )
            elif len(transaction.code) != 6 and not (
                len(transaction.code) == 5 and transaction.code.startswith("0")
            ):
                errors.append(
                    f"Transaction {index + 1}: Code must be 6 digits (or 5 digits starting with 0 for Hong Kong stocks)"
                )
            elif len(transaction.code) > 6:
                # Allow longer codes for international stocks (e.g., TSLA)
                warnings.append(
                    f"Transaction {index + 1}: Non-standard investment code length"
                )

            # Validate date is not in future (allow some tolerance)
            if transaction.date > datetime.now().date():
                warnings.append(f"Transaction {index + 1}: Date is in the future")

            # Validate type-specific requirements
            if transaction.type == TransactionType.BUY:
                if transaction.quantity <= 0:
                    errors.append(
                        f"Transaction {index + 1}: Buy quantity must be positive"
                    )
                if transaction.unit_price <= 0:
                    errors.append(
                        f"Transaction {index + 1}: Buy unit price must be positive"
                    )
                if transaction.total_amount <= 0:
                    errors.append(
                        f"Transaction {index + 1}: Buy total amount must be positive"
                    )

            elif transaction.type == TransactionType.SELL:
                if transaction.quantity <= 0:
                    errors.append(
                        f"Transaction {index + 1}: Sell quantity must be positive"
                    )
                if transaction.unit_price <= 0:
                    errors.append(
                        f"Transaction {index + 1}: Sell unit price must be positive"
                    )

                # For sell transactions, total_amount may be less due to fees
                if transaction.total_amount <= 0:
                    errors.append(
                        f"Transaction {index + 1}: Sell total amount must be positive"
                    )

            elif transaction.type == TransactionType.DIVIDEND:
                # Determine dividend type based on transaction context
                # Cash dividend: quantity=0, total_amount>0
                # Stock dividend/reinvestment: quantity>0 (unit_price can be 0 for free shares)
                if transaction.quantity == 0 and transaction.total_amount > 0:
                    # Cash dividend - valid
                    pass
                elif transaction.quantity > 0:
                    # Stock dividend or reinvestment - shares added (price can be 0)
                    # This is valid even if unit_price is 0 (free shares from dividend)
                    pass
                elif transaction.total_amount > 0:
                    # Cash dividend with quantity=0 - valid
                    pass
                else:
                    errors.append(
                        f"Transaction {index + 1}: Dividend must have either positive amount (cash) or positive quantity (stock)"
                    )

            # Validate reasonable price ranges
            if (
                transaction.unit_price > 10000
            ):  # ¥10,000 per share seems unreasonably high
                warnings.append(
                    f"Transaction {index + 1}: Very high unit price ({transaction.unit_price})"
                )
            elif (
                transaction.unit_price < 0.01
                and transaction.type != TransactionType.DIVIDEND
            ):
                warnings.append(
                    f"Transaction {index + 1}: Very low unit price ({transaction.unit_price})"
                )

            # Validate reasonable quantities
            if (
                transaction.quantity > 1000000
            ):  # 1M+ shares/fund units seems unusually high
                warnings.append(
                    f"Transaction {index + 1}: Very large quantity ({transaction.quantity})"
                )

        except Exception as e:
            errors.append(f"Transaction {index + 1}: Validation error - {e}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    async def validate_transaction_consistency(
        self, transactions: TransactionList
    ) -> ValidationResult:
        """Validate consistency across all transactions."""
        errors = []
        warnings = []

        try:
            # Check for duplicate transactions
            duplicates = self._find_duplicate_transactions(transactions.transactions)
            if duplicates:
                warnings.extend(
                    [f"Potential duplicate transaction: {dup}" for dup in duplicates]
                )

            # Check chronological order
            unsorted = self._find_unsorted_transactions(transactions.transactions)
            if unsorted:
                errors.append(
                    f"Transactions are not in chronological order: {unsorted}"
                )

            # Validate code consistency
            invalid_codes = self._validate_investment_codes(transactions.transactions)
            if invalid_codes:
                errors.extend(
                    [f"Invalid investment code: {code}" for code in invalid_codes]
                )

            # Check for logical issues
            logical_issues = self._check_logical_consistency(transactions)
            errors.extend(logical_issues)

        except Exception as e:
            errors.append(f"Consistency validation error: {e}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _find_duplicate_transactions(
        self, transactions: list[Transaction]
    ) -> list[str]:
        """Find potential duplicate transactions."""
        seen = set()
        duplicates = []

        for tx in transactions:
            # Create a unique key for the transaction
            key = f"{tx.code}-{tx.date}-{tx.type}-{tx.quantity}-{tx.unit_price}-{tx.total_amount}"
            if key in seen:
                duplicates.append(f"{tx.code} on {tx.date}")
            else:
                seen.add(key)

        return duplicates

    def _find_unsorted_transactions(self, transactions: list[Transaction]) -> list[str]:
        """Find transactions that are not in chronological order."""
        unsorted = []
        previous_date = None

        for tx in transactions:
            if previous_date and tx.date < previous_date:
                unsorted.append(f"{tx.code} on {tx.date} comes after {previous_date}")
            previous_date = tx.date

        return unsorted

    def _validate_investment_codes(self, transactions: list[Transaction]) -> list[str]:
        """Validate investment code formats."""
        invalid_codes = set()
        seen_codes = set()

        for tx in transactions:
            # Check if code follows expected patterns
            code = tx.code
            if not code.isdigit():
                # Allow alphanumeric codes for international stocks (e.g., TSLA)
                if code.isalpha():
                    continue  # Allow alphabetic codes for international stocks
                invalid_codes.add(code)
                continue
            elif len(code) != 6 and not (len(code) == 5 and code.startswith("0")):
                # Allow non-standard codes (like TSLA) for international stocks
                if len(code) > 6:
                    continue  # Allow longer codes for international stocks
                invalid_codes.add(code)
                continue

            seen_codes.add(code)

        # Warn about single investment codes (might be typos)
        for code in seen_codes:
            count = sum(1 for tx in transactions if tx.code == code)
            if count == 1:
                # This could be normal or it could be a typo
                pass

        return list(invalid_codes)

    def _check_logical_consistency(self, transactions: TransactionList) -> list[str]:
        """Check for logical consistency issues."""
        errors = []

        # Group transactions by code and check for negative positions
        codes = transactions.get_codes()

        for code in codes:
            code_transactions = transactions.filter_by_code(code).transactions
            position_issues = self._check_code_position_consistency(code_transactions)
            errors.extend(position_issues)

        return errors

    def _check_code_position_consistency(
        self, transactions: list[Transaction]
    ) -> list[str]:
        """Check if transactions lead to negative positions for a code."""
        errors = []
        position = 0.0

        # Sort by date to check position in chronological order
        sorted_transactions = sorted(transactions, key=lambda tx: tx.date)

        for tx in sorted_transactions:
            if tx.type == TransactionType.BUY:
                position += tx.quantity
            elif tx.type == TransactionType.SELL:
                position -= tx.quantity
                if position < -0.01:  # Allow small floating point errors
                    errors.append(
                        f"Negative position for {tx.code} after selling on {tx.date}"
                    )
            elif tx.type == TransactionType.DIVIDEND and tx.quantity > 0:
                # Stock dividend adds shares
                position += tx.quantity

        return errors

    def _is_reasonable_stock_code(self, code: str) -> bool:
        """Check if code follows typical Chinese stock code patterns."""
        if len(code) != 6 or not code.isdigit():
            return False

        # Shanghai Stock Exchange (starts with 6)
        if code.startswith("6"):
            return True

        # Shenzhen Stock Exchange (starts with 0 or 3)
        if code.startswith(("0", "3")):
            return True

        # Beijing Stock Exchange (starts with 8 or 4)
        if code.startswith(("8", "4")):
            return True

        return False

    def _is_reasonable_fund_code(self, code: str) -> bool:
        """Check if code follows typical Chinese fund code patterns."""
        if len(code) != 6 or not code.isdigit():
            return False

        # Common fund prefixes
        fund_prefixes = [
            "110",
            "161",
            "163",
            "164",
            "165",
            "166",
            "167",
            "168",
            "169",  # 华安
            "501",
            "502",
            "503",
            "504",
            "505",
            "506",
            "507",
            "508",
            "509",  # 华宝
        ]

        return any(code.startswith(prefix) for prefix in fund_prefixes)
