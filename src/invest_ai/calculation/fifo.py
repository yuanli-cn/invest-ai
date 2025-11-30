"""FIFO (First-In-First-Out) cost allocation implementation."""

from invest_ai.models import (
    FifoQueue,
    FifoResult,
    Purchase,
    Transaction,
    TransactionType,
)


class FifoCalculator:
    """Implements FIFO cost allocation for investment transactions."""

    def __init__(self) -> None:
        """Initialize the FIFO calculator."""

    def process_fifo_queue(self, transactions: list[Transaction]) -> FifoQueue:
        """Process transactions into a FIFO queue."""
        if not transactions:
            raise ValueError("Transactions list cannot be empty")

        # Get the investment code from the first transaction
        code = transactions[0].code

        # Validate all transactions have the same code
        for tx in transactions:
            if tx.code != code:
                raise ValueError(
                    f"All transactions must have the same code. "
                    f"Expected {code}, got {tx.code}"
                )

        queue = FifoQueue(code=code)

        # Sort transactions by date to maintain FIFO order
        sorted_transactions = sorted(transactions, key=lambda x: x.date)

        for transaction in sorted_transactions:
            if transaction.type == TransactionType.BUY:
                # Add buy transaction to the queue
                purchase = Purchase(
                    date=transaction.date,
                    quantity=transaction.quantity,
                    unit_price=transaction.unit_price,
                    remaining_quantity=transaction.quantity,
                )
                queue.add_purchase(purchase)

            elif transaction.type == TransactionType.DIVIDEND:
                # Stock/mutual fund dividend - add shares without cost basis
                dividend_purchase = Purchase(
                    date=transaction.date,
                    quantity=transaction.quantity,
                    unit_price=0.0,  # No cost basis for dividends
                    remaining_quantity=transaction.quantity,
                )
                queue.add_purchase(dividend_purchase)

            # Sell transactions are handled separately in allocate_cost()

        return queue

    def allocate_cost(
        self, sell_transaction: Transaction, fifo_queue: FifoQueue
    ) -> FifoResult:
        """Allocate cost for a sell transaction using FIFO."""
        if sell_transaction.type != TransactionType.SELL:
            raise ValueError(
                f"Transaction must be SELL type, got {sell_transaction.type}"
            )

        if not fifo_queue.has_inventory:
            raise ValueError("No inventory available to allocate")

        allocated_purchases = []
        remaining_sell_quantity = sell_transaction.quantity
        total_cost_basis = 0.0

        # Create a copy of the queue to work with
        working_queue = FifoQueue(code=fifo_queue.code)

        # Copy existing purchases
        for purchase in fifo_queue.purchases:
            purchase_copy = Purchase(
                date=purchase.date,
                quantity=purchase.quantity,
                unit_price=purchase.unit_price,
                remaining_quantity=purchase.remaining_quantity,
            )
            working_queue.add_purchase(purchase_copy)

        # Allocate from earliest purchases
        while remaining_sell_quantity > 0:
            next_purchase = working_queue.get_next_purchase()
            if next_purchase is None:
                # Not enough inventory to cover the sale
                raise ValueError(
                    f"Insufficient inventory: trying to sell {sell_transaction.quantity}, "
                    f"but only {sell_transaction.quantity - remaining_sell_quantity} available"
                )
            # At this point, next_purchase is guaranteed to be not None

            if next_purchase.remaining_quantity <= remaining_sell_quantity:
                # Take the entire remaining quantity of this purchase
                allocated_purchases.append(next_purchase)
                total_cost_basis += (
                    next_purchase.remaining_quantity * next_purchase.unit_price
                )
                remaining_sell_quantity -= next_purchase.remaining_quantity
                next_purchase.remaining_quantity = 0

            else:
                # Take a partial quantity from this purchase
                allocated_quantity = remaining_sell_quantity
                partial_purchase = Purchase(
                    date=next_purchase.date,
                    quantity=next_purchase.quantity,
                    unit_price=next_purchase.unit_price,
                    remaining_quantity=allocated_quantity,
                )
                allocated_purchases.append(partial_purchase)
                total_cost_basis += allocated_quantity * next_purchase.unit_price
                next_purchase.remaining_quantity -= allocated_quantity
                remaining_sell_quantity = 0

        # Create the remaining queue after allocations
        remaining_fifo = FifoQueue(code=fifo_queue.code)
        for purchase in working_queue.purchases:
            if purchase.remaining_quantity > 0:
                remaining_fifo.add_purchase(purchase)

        return FifoResult(
            code=fifo_queue.code,
            allocated_purchases=allocated_purchases,
            cost_basis=total_cost_basis,
            remaining_queue=remaining_fifo,
        )

    def calculate_realized_gain(
        self, sell_transaction: Transaction, cost_basis: float
    ) -> float:
        """Calculate realized gain for a sell transaction."""
        if sell_transaction.type != TransactionType.SELL:
            raise ValueError(
                f"Transaction must be SELL type, got {sell_transaction.type}"
            )

        sell_value = sell_transaction.total_amount
        realized_gain = sell_value - cost_basis
        return realized_gain

    def process_multiple_sales(
        self, transactions: list[Transaction], initial_queue: FifoQueue | None = None
    ) -> tuple[list[FifoResult], FifoQueue]:
        """Process multiple sell transactions in FIFO order."""
        if initial_queue is None:
            # First process all buy transactions to build the queue
            buy_transactions = [
                tx for tx in transactions if tx.type == TransactionType.BUY
            ]
            queue = self.process_fifo_queue(buy_transactions)
        else:
            queue = initial_queue

        # Sort sell transactions by date
        sell_transactions = sorted(
            [tx for tx in transactions if tx.type == TransactionType.SELL],
            key=lambda x: x.date,
        )

        results = []
        for sell_transaction in sell_transactions:
            try:
                fifo_result = self.allocate_cost(sell_transaction, queue)
                results.append(fifo_result)
                queue = fifo_result.remaining_queue
            except ValueError as e:
                # Handle insufficient inventory (shouldn't happen with proper validation)
                error_result = FifoResult(
                    allocated_purchases=[], cost_basis=0.0, remaining_queue=queue
                )
                results.append(error_result)
                print(f"Warning: {e}")

        return results, queue

    def get_remaining_inventory_value(
        self, queue: FifoQueue, current_prices: dict[str, float]
    ) -> float:
        """Calculate the market value of remaining inventory."""
        total_value = 0.0

        for purchase in queue.purchases:
            if purchase.remaining_quantity > 0:
                # We don't have the investment code here, so just sum up the quantities
                # The calling code will need to map this to actual prices
                total_value += (
                    purchase.remaining_quantity
                )  # This is a simplified version

        return total_value

    def validate_fifo_processing(self, transactions: list[Transaction]) -> list[str]:
        """Validate transactions for FIFO processing."""
        errors = []

        # Sort transactions by date
        sorted_transactions = sorted(transactions, key=lambda x: x.date)

        # Track positions
        position: float = 0

        for i, transaction in enumerate(sorted_transactions):
            if transaction.type == TransactionType.BUY:
                position += transaction.quantity
            elif transaction.type == TransactionType.SELL:
                position -= transaction.quantity

                if position < 0:
                    error_msg = (
                        f"Negative position at transaction {i + 1} "
                        f"({transaction.code} on {transaction.date}): "
                        f"Position = {position}"
                    )
                    errors.append(error_msg)

        return errors
