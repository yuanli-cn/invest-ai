"""XIRR (Extended Internal Rate of Return) calculation.

XIRR is the standard method for calculating annualized returns on investments
with irregular cash flows. It considers the timing of each cash flow.
"""

from datetime import date


def calculate_xirr(
    cashflows: list[tuple[date, float]],
    max_iterations: int = 100,
    tolerance: float = 1e-6,
) -> float:
    """Calculate XIRR (Extended Internal Rate of Return).

    XIRR finds the discount rate that makes the Net Present Value (NPV) of
    all cash flows equal to zero.

    Args:
        cashflows: List of (date, amount) tuples.
            - Negative amounts = cash outflows (investments/purchases)
            - Positive amounts = cash inflows (sales/dividends/final value)
        max_iterations: Maximum iterations for Newton-Raphson method.
        tolerance: Convergence tolerance.

    Returns:
        Annualized return rate as percentage (e.g., 15.5 for 15.5%).
        Returns 0.0 if calculation fails or no valid cash flows.

    Example:
        >>> cashflows = [
        ...     (date(2024, 1, 1), -10000),   # Buy
        ...     (date(2024, 6, 15), -5000),   # Add more
        ...     (date(2024, 12, 31), 16500),  # Final value
        ... ]
        >>> calculate_xirr(cashflows)
        10.5  # Approximately 10.5% annualized return
    """
    if not cashflows or len(cashflows) < 2:
        return 0.0

    # Filter out zero cash flows
    cashflows = [(d, amt) for d, amt in cashflows if amt != 0]
    if len(cashflows) < 2:
        return 0.0

    # Check if there are both positive and negative cash flows
    has_negative = any(amt < 0 for _, amt in cashflows)
    has_positive = any(amt > 0 for _, amt in cashflows)
    if not has_negative or not has_positive:
        return 0.0

    # Sort by date
    cashflows = sorted(cashflows, key=lambda x: x[0])
    min_date = cashflows[0][0]

    # Calculate years from first date for each cash flow
    def years_from_start(d: date) -> float:
        return (d - min_date).days / 365.0

    years = [years_from_start(d) for d, _ in cashflows]
    amounts = [amt for _, amt in cashflows]

    def npv(rate: float) -> float:
        """Calculate Net Present Value at given rate."""
        if rate <= -1:
            return float("inf")
        return sum(amt / ((1 + rate) ** yr) for amt, yr in zip(amounts, years))

    def npv_derivative(rate: float) -> float:
        """Calculate derivative of NPV with respect to rate."""
        if rate <= -1:
            return float("inf")
        return sum(
            -yr * amt / ((1 + rate) ** (yr + 1)) for amt, yr in zip(amounts, years)
        )

    # Newton-Raphson method with initial guess of 10%
    rate = 0.1

    for _ in range(max_iterations):
        npv_value = npv(rate)
        npv_deriv = npv_derivative(rate)

        if abs(npv_deriv) < 1e-10:
            # Derivative too small, try bisection
            break

        new_rate = rate - npv_value / npv_deriv

        # Bound the rate to reasonable values
        new_rate = max(-0.99, min(new_rate, 10.0))

        if abs(new_rate - rate) < tolerance:
            return new_rate * 100  # Convert to percentage

        rate = new_rate

    # Fallback to bisection method if Newton-Raphson fails
    return _bisection_xirr(amounts, years, tolerance) * 100


def _bisection_xirr(
    amounts: list[float],
    years: list[float],
    tolerance: float = 1e-6,
) -> float:
    """Fallback bisection method for XIRR calculation."""
    low, high = -0.99, 10.0

    def npv(rate: float) -> float:
        return sum(amt / ((1 + rate) ** yr) for amt, yr in zip(amounts, years))

    # Check if solution exists in range
    if npv(low) * npv(high) > 0:
        return 0.0

    for _ in range(100):
        mid = (low + high) / 2
        npv_mid = npv(mid)

        if abs(npv_mid) < tolerance or (high - low) / 2 < tolerance:
            return mid

        if npv(low) * npv_mid < 0:
            high = mid
        else:
            low = mid

    return (low + high) / 2


def build_annual_cashflows(
    start_date: date,
    end_date: date,
    start_value: float,
    end_value: float,
    transactions: list[tuple[date, str, float]],
) -> list[tuple[date, float]]:
    """Build cash flow list for annual XIRR calculation.

    Args:
        start_date: Year start date (for initial portfolio value).
        end_date: Year end date (for final portfolio value).
        start_value: Portfolio value at start of year.
        end_value: Portfolio value at end of year.
        transactions: List of (date, type, amount) tuples.
            type: 'BUY', 'SELL', or 'DIVIDEND'

    Returns:
        List of (date, amount) tuples for XIRR calculation.
    """
    cashflows: list[tuple[date, float]] = []

    # Start value as negative (virtual investment at year start)
    if start_value > 0:
        cashflows.append((start_date, -start_value))

    # Process transactions during the year
    for tx_date, tx_type, amount in transactions:
        if tx_type == "BUY":
            # Buy = cash outflow (negative)
            cashflows.append((tx_date, -amount))
        elif tx_type in ("SELL", "DIVIDEND"):
            # Sell/Dividend = cash inflow (positive)
            cashflows.append((tx_date, amount))

    # End value as positive (virtual liquidation at year end)
    if end_value > 0:
        cashflows.append((end_date, end_value))

    return cashflows


def build_history_cashflows(
    transactions: list[tuple[date, str, float]],
    end_date: date,
    current_value: float,
) -> list[tuple[date, float]]:
    """Build cash flow list for history (all-time) XIRR calculation.

    Args:
        transactions: List of (date, type, amount) tuples.
        end_date: Current date (for final portfolio value).
        current_value: Current portfolio value.

    Returns:
        List of (date, amount) tuples for XIRR calculation.
    """
    cashflows: list[tuple[date, float]] = []

    # Process all transactions
    for tx_date, tx_type, amount in transactions:
        if tx_type == "BUY":
            cashflows.append((tx_date, -amount))
        elif tx_type in ("SELL", "DIVIDEND"):
            cashflows.append((tx_date, amount))

    # Current value as final cash inflow
    if current_value > 0:
        cashflows.append((end_date, current_value))

    return cashflows
