"""Main CLI entry point."""

import argparse
import asyncio
import sys
from datetime import date
from typing import cast

from invest_ai.models import (
    AnnualResult,
    FilterCriteria,
    HistoryResult,
    InvestmentType,
    PriceData,
    TransactionList,
)

from ..calculation.engine import CalculationEngine
from ..config.settings import load_settings
from ..market.price_fetcher import PriceFetcher
from ..reporting.reports import ReportGenerator
from ..transaction.filter import TransactionFilter
from ..transaction.loader import TransactionLoader
from ..transaction.validator import TransactionValidator
from .arguments import parse_arguments, print_help_summary, validate_arguments


class CLIController:
    """Main CLI controller."""

    def __init__(self) -> None:
        """Initialize the CLI controller."""
        self.settings = load_settings()
        self.loader = TransactionLoader()
        self.validator = TransactionValidator()
        self.filter = TransactionFilter()
        self.engine = CalculationEngine()
        self.reporter = ReportGenerator()
        self.price_fetcher = PriceFetcher()

    async def run(self, args: list[str] | None = None) -> int:
        """Run the CLI application."""
        try:
            # Parse arguments (pass args to allow testing with custom arguments)
            parsed_args = parse_arguments(args)

            # If no arguments provided, help was shown, return success
            if parsed_args is None:
                return 0

            # Validate arguments
            if not validate_arguments(parsed_args):
                return 1

            # Execute calculation
            result = await self.execute_calculation(parsed_args)

            if result is None:
                return 1

            # Format and display output
            await self.display_results(result, parsed_args)

            return 0

        except KeyboardInterrupt:
            print("\nOperation cancelled by user", file=sys.stderr)
            return 130
        except Exception as e:
            if self.settings.debug:
                import traceback

                traceback.print_exc()
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1

    def _get_arg(self, args: argparse.Namespace | dict, key: str, default=None):
        """Get argument value from either dict or Namespace."""
        if isinstance(args, dict):
            return args.get(key, default)
        return getattr(args, key, default)

    async def execute_calculation(
        self, args: argparse.Namespace | dict
    ) -> AnnualResult | HistoryResult | None:
        """Execute the calculation based on arguments."""
        try:
            # Extract arguments
            data_path = self._get_arg(args, "data")
            type_value = self._get_arg(args, "type")
            transactions_provided = self._get_arg(args, "transactions")
            mock_prices = self._get_arg(args, "mock_prices")
            verbose = self._get_arg(args, "verbose")
            code_value = self._get_arg(args, "code")
            year_value = self._get_arg(args, "year")

            # Convert string year to int if needed
            if isinstance(year_value, str):
                year_value = int(year_value)

            # Load transactions
            if transactions_provided:
                transactions = transactions_provided
            else:
                if not data_path:
                    data_path = f"data/{type_value}.yaml" if type_value else None
                    if not data_path:
                        raise ValueError("Data path is required")
                transactions = await self.loader.load_transactions(data_path)

            if not transactions:
                print("No transactions found in the data file")
                return None

            # Validate transactions
            validation_result = await self.validator.validate_transactions(transactions)
            if not validation_result.is_valid:
                print("Transaction validation failed:", file=sys.stderr)
                for error in validation_result.errors:
                    print(f"  - {error}", file=sys.stderr)
                return None

            if verbose and validation_result.warnings:
                print("Validation warnings:")
                for warning in validation_result.warnings:
                    print(f"  - {warning}")

            # Determine investment type
            investment_type = InvestmentType(type_value)

            criteria = FilterCriteria(
                investment_type=investment_type,
                code=code_value,
                year=year_value,
            )

            # Filter transactions
            filtered_transactions = await self.filter.filter_transactions(
                transactions, criteria
            )

            # For annual calculations, also get pre-year transactions
            pre_year_transactions = TransactionList(transactions=[])
            if year_value:
                pre_criteria = FilterCriteria(
                    investment_type=investment_type,
                    code=code_value,
                    before_year=year_value,
                )
                pre_year_transactions = await self.filter.filter_transactions(
                    transactions, pre_criteria
                )

            # Execute calculation based on scenario
            if year_value and code_value:
                # Specific investment, specific year
                # Fetch year-start and year-end prices if not provided
                prices_for_annual = mock_prices or {}
                if not prices_for_annual:
                    prices_for_annual = await self._fetch_annual_prices(
                        [code_value], year_value, investment_type
                    )
                annual_result = await self.engine.calculate_annual_returns(
                    pre_year_transactions, filtered_transactions, year_value, code_value, prices_for_annual
                )
                return annual_result
            elif year_value and not code_value:
                # All investments, specific year
                # Get all codes that have transactions
                all_codes = set(pre_year_transactions.get_codes()) | set(filtered_transactions.get_codes())
                prices_for_annual = mock_prices or {}
                if not prices_for_annual and all_codes:
                    prices_for_annual = await self._fetch_annual_prices(
                        list(all_codes), year_value, investment_type
                    )
                annual_result = await self.engine.calculate_portfolio_annual_returns(
                    pre_year_transactions, filtered_transactions, year_value, prices_for_annual
                )
                return annual_result
            elif not year_value and code_value:
                # Specific investment, full history
                # Fetch current prices if not provided via mock_prices
                current_prices = mock_prices or {}
                if not current_prices:
                    current_prices = await self._fetch_current_prices_for_codes(
                        [code_value], investment_type
                    )
                history_result = await self.engine.calculate_single_investment_history(
                    filtered_transactions, code_value, current_prices
                )
                return history_result
            else:
                # All investments, full history
                # Fetch current prices if not provided via mock_prices
                current_prices = mock_prices or {}
                if not current_prices:
                    codes = filtered_transactions.get_codes()
                    current_prices = await self._fetch_current_prices_for_codes(
                        codes, investment_type
                    )
                history_result = await self.engine.calculate_portfolio_history(
                    filtered_transactions, current_prices
                )
                return history_result

        except Exception as e:
            print(f"Error during calculation: {e}", file=sys.stderr)
            if self.settings.debug:
                import traceback

                traceback.print_exc()
            return None

    async def display_results(
        self, result: AnnualResult | HistoryResult, args: argparse.Namespace
    ) -> None:
        """Display calculation results."""
        try:
            if args.format == "json":
                # Convert result to dict for JSON format
                result_dict = (
                    result.model_dump()
                    if hasattr(result, "model_dump")
                    else dict(result)
                )
                output = await self.reporter.format_json_report(result_dict)
            else:
                if args.year:
                    # This should be an AnnualResult
                    annual_result = cast(AnnualResult, result)
                    # Simple clean output
                    if args.code:
                        output = f"""
┌─────────────────────────────────────┐
│ {args.type.upper()} {args.code} - {annual_result.year}
├─────────────────────────────────────┤
│ Initial Investment: ¥{annual_result.start_value:,.2f}
│ Current Value:     ¥{annual_result.end_value:,.2f}
│ Net Gain/Loss:     ¥{annual_result.net_gain:,.2f}
│ Return Rate:       {annual_result.return_rate:.2f}%
│ Dividends:         ¥{annual_result.dividends:,.2f}
└─────────────────────────────────────┘"""
                    else:
                        output = f"""
┌─────────────────────────────────────┐
│ PORTFOLIO - {annual_result.year}
├─────────────────────────────────────┤
│ Start Value:       ¥{annual_result.start_value:,.2f}
│ End Value:         ¥{annual_result.end_value:,.2f}
│ Dividends:         ¥{annual_result.dividends:,.2f}
│ Capital Gain:      ¥{annual_result.capital_gain:,.2f}
│ Total Gain/Loss:   ¥{annual_result.net_gain:,.2f}
│ Return Rate:       {annual_result.return_rate:.2f}%
└─────────────────────────────────────┘"""
                else:
                    # This should be a HistoryResult
                    history_result = cast(HistoryResult, result)
                    # Simple clean history output
                    if args.code:
                        output = f"""
┌─────────────────────────────────────┐
│ {args.type.upper()} {args.code} - History
├─────────────────────────────────────┤
│ Total Invested:    ¥{history_result.total_invested:,.2f}
│ Current Value:     ¥{history_result.current_value:,.2f}
│ Total P&L:         ¥{history_result.total_gain:,.2f}
│ Return Rate:       {history_result.return_rate:.2f}%
└─────────────────────────────────────┘"""
                    else:
                        output = f"""
┌─────────────────────────────────────┐
│ PORTFOLIO HISTORY
├─────────────────────────────────────┤
│ Total Invested:    ¥{history_result.total_invested:,.2f}
│ Current Value:     ¥{history_result.current_value:,.2f}
│ Total P&L:         ¥{history_result.total_gain:,.2f}
│ Return Rate:       {history_result.return_rate:.2f}%
└─────────────────────────────────────┘"""

            print(output)

        except Exception as e:
            print(f"Error formatting results: {e}", file=sys.stderr)

    def _convert_mock_prices(self, mock_prices: dict | None) -> dict:
        """Convert mock_prices from list format to single PriceData format."""
        if not mock_prices:
            return {}
        result = {}
        for code, price_list in mock_prices.items():
            if isinstance(price_list, list) and price_list:
                # Get the latest price (first in list, assuming sorted)
                result[code] = price_list[0]
            else:
                result[code] = price_list
        return result

    async def _fetch_current_prices_for_codes(
        self, codes: list[str], investment_type: InvestmentType
    ) -> dict:
        """Fetch current prices for given codes using API.
        
        Args:
            codes: List of investment codes
            investment_type: Type of investment (stock or fund)
            
        Returns:
            Dictionary mapping code to PriceData
        """
        if not codes:
            return {}
        
        try:
            if not self.price_fetcher.is_available(investment_type):
                print(
                    f"Warning: Price fetcher not available for {investment_type.value}",
                    file=sys.stderr,
                )
                return {}
            
            prices = await self.price_fetcher.fetch_current_prices(codes, investment_type)
            return prices
        except Exception as e:
            print(f"Warning: Failed to fetch prices: {e}", file=sys.stderr)
            return {}

    async def _fetch_annual_prices(
        self,
        codes: list[str],
        year: int,
        investment_type: InvestmentType,
    ) -> dict[str, dict[str, PriceData]]:
        """Fetch year-start and year-end prices for annual calculation.
        
        Args:
            codes: List of investment codes
            year: The year to get prices for
            investment_type: Type of investment (stock or fund)
            
        Returns:
            Dictionary with 'year_start' and 'year_end' keys, each containing
            a dict mapping code to PriceData
        """
        from datetime import datetime
        from ..market.trading_days import get_year_start_trading_day, get_year_end_trading_day
        
        if not codes:
            return {"year_start": {}, "year_end": {}}
        
        try:
            if not self.price_fetcher.is_available(investment_type):
                print(
                    f"Warning: Price fetcher not available for {investment_type.value}",
                    file=sys.stderr,
                )
                return {"year_start": {}, "year_end": {}}
            
            # Get trading day dates
            year_start_date = get_year_start_trading_day(year)
            
            # For current year, use today; otherwise use year end
            current_year = datetime.now().year
            if year >= current_year:
                year_end_date = date.today()
            else:
                year_end_date = get_year_end_trading_day(year)
            
            # Fetch prices for both dates
            year_start_prices: dict[str, PriceData] = {}
            year_end_prices: dict[str, PriceData] = {}
            
            if investment_type == InvestmentType.FUND:
                # Fund: Use parallel requests (EastMoney has no strict rate limit)
                import asyncio
                
                async def fetch_fund_price(code: str, target_date: date, label: str) -> tuple[str, str, PriceData | None]:
                    try:
                        nav_data = await self.price_fetcher.eastmoney_client.fetch_fund_nav(code, target_date)
                        return code, label, PriceData(
                            code=code,
                            price_date=nav_data.nav_date,
                            price_value=nav_data.nav,
                            source="eastmoney"
                        )
                    except Exception as e:
                        print(f"Warning: Failed to fetch {label} price for {code}: {e}", file=sys.stderr)
                        return code, label, None
                
                # Create tasks for all codes and both dates
                tasks = []
                for code in codes:
                    tasks.append(fetch_fund_price(code, year_start_date, "year_start"))
                    tasks.append(fetch_fund_price(code, year_end_date, "year_end"))
                
                results = await asyncio.gather(*tasks)
                for code, label, price_data in results:
                    if price_data:
                        if label == "year_start":
                            year_start_prices[code] = price_data
                        else:
                            year_end_prices[code] = price_data
            else:
                # Stock: Sequential requests (Tushare has rate limit)
                assert self.price_fetcher.tushare_client is not None
                for code in codes:
                    try:
                        price_data = await self.price_fetcher.tushare_client.fetch_stock_price(code, year_start_date)
                        year_start_prices[code] = price_data
                    except Exception as e:
                        print(f"Warning: Failed to fetch year-start price for {code}: {e}", file=sys.stderr)
                    
                    try:
                        price_data = await self.price_fetcher.tushare_client.fetch_stock_price(code, year_end_date)
                        year_end_prices[code] = price_data
                    except Exception as e:
                        print(f"Warning: Failed to fetch year-end price for {code}: {e}", file=sys.stderr)
            
            return {
                "year_start": year_start_prices,
                "year_end": year_end_prices,
            }
            
        except Exception as e:
            print(f"Warning: Failed to fetch annual prices: {e}", file=sys.stderr)
            return {"year_start": {}, "year_end": {}}

    def _get_current_prices(self, codes: list[str]) -> dict[str, float]:
        """Get current market prices for given investment codes."""
        import asyncio
        import sys

        from ..market.price_fetcher import PriceFetcher

        async def fetch_prices():
            fetcher = PriceFetcher()
            prices = {}
            for code in codes:
                try:
                    if (
                        code.startswith("0")
                        or code.startswith("3")
                        or code.startswith("6")
                    ):
                        # Mainland stock
                        client = fetcher.tushare_client
                        if client:
                            price_data = await client.fetch_current_price(code)
                            prices[code] = price_data.close if price_data else 100.0
                    elif (
                        code.startswith("5") or len(code) == 6 and code.startswith("1")
                    ):
                        # Fund
                        client = fetcher.eastmoney_client
                        if client:
                            nav_data = await client.fetch_fund_nav(code)
                            prices[code] = nav_data.nav if nav_data else 1.0
                    else:
                        # Other/International stocks - use default prices
                        prices[code] = 100.0
                except Exception as err:
                    # Default price for failed API calls
                    print(
                        f"Warning: Failed to fetch price for {code}: {err}",
                        file=sys.stderr,
                    )
                    prices[code] = 100.0
            return prices

        # Run the async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(fetch_prices())


def main() -> int:
    """Main entry point."""
    controller = CLIController()

    # Check for special cases first
    if len(sys.argv) == 1:
        print_help_summary()
        return 0

    # Run the application
    return asyncio.run(controller.run())


if __name__ == "__main__":
    sys.exit(main())
