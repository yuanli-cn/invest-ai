"""Unified price fetching interface."""

import asyncio
from datetime import date

from invest_ai.config import create_api_config
from invest_ai.models import (
    InvestmentType,
    NavData,
    PriceData,
    PriceResponse,
)

from .fund_client import EastMoneyClient
from .stock_client import TushareClient


class PriceFetcher:
    """Unified interface for fetching market prices and NAVs."""

    def __init__(self, tushare_token: str | None = None) -> None:
        """Initialize the price fetcher."""
        self.config = create_api_config()
        self.tushare_client: TushareClient | None = None
        self.eastmoney_client: EastMoneyClient = EastMoneyClient()

        # Initialize clients based on configuration
        if self.config.tushare.is_configured or tushare_token:
            try:
                self.tushare_client = TushareClient(tushare_token)
            except ValueError as e:
                print(f"Warning: Tushare client initialization failed: {e}")

    def is_available(self, investment_type: InvestmentType) -> bool:
        """Check if price fetching is available for the investment type."""
        if investment_type == InvestmentType.STOCK:
            return bool(self.tushare_client)
        else:  # InvestmentType.FUND
            return True  # East Money is always available

    async def fetch_current_prices(
        self, codes: list[str], investment_type: InvestmentType
    ) -> dict[str, PriceData]:
        """Fetch current prices for multiple codes."""
        if investment_type == InvestmentType.STOCK:
            if not self.tushare_client:
                raise ValueError("Tushare client not available for stock data")
            return await self.tushare_client.fetch_current_prices(codes)

        elif investment_type == InvestmentType.FUND:
            # Use East Money for fund data, convert NAV to price
            fund_prices = await self.eastmoney_client.fetch_current_prices_as_nav(codes)
            return fund_prices

        else:
            raise ValueError(f"Unsupported investment type: {investment_type}")

    async def fetch_historical_prices(
        self, codes: list[str], dates: list[date], investment_type: InvestmentType
    ) -> dict[str, list[PriceData]]:
        """Fetch historical prices for multiple codes and dates."""
        if investment_type == InvestmentType.STOCK:
            if not self.tushare_client:
                raise ValueError("Tushare client not available for stock data")
            return await self.tushare_client.fetch_historical_prices(codes, dates)

        elif investment_type == InvestmentType.FUND:
            # Use East Money for fund data, convert NAV to price
            fund_prices = await self.eastmoney_client.fetch_fund_prices_as_nav(
                codes, dates
            )
            return fund_prices

        else:
            raise ValueError(f"Unsupported investment type: {investment_type}")

    async def fetch_fund_nav(self, code: str, target_date: date) -> NavData:
        """Fetch specific fund NAV (returns NavData, not PriceData)."""
        return await self.eastmoney_client.fetch_fund_nav(code, target_date)

    async def fetch_price_response(
        self, codes: list[str], dates: list[date], investment_type: InvestmentType
    ) -> PriceResponse:
        """Fetch prices and return as PriceResponse object."""
        price_data = await self.fetch_historical_prices(codes, dates, investment_type)
        return PriceResponse(data=price_data)

    async def validate_codes(
        self, codes: list[str], investment_type: InvestmentType
    ) -> dict[str, bool]:
        """Validate investment codes."""
        results = {}

        if investment_type == InvestmentType.STOCK:
            if not self.tushare_client:
                # Default to invalid if client not available
                return dict.fromkeys(codes, False)

            # Validate in parallel
            sem = asyncio.Semaphore(10)

            async def validate_single(code: str) -> tuple[str, bool]:
                async with sem:
                    assert self.tushare_client is not None  # Type checker guarantee
                    return code, await self.tushare_client.validate_code(code)

            tasks = [validate_single(code) for code in codes]
            completed = await asyncio.gather(*tasks, return_exceptions=True)

            for result in completed:
                if isinstance(result, tuple):
                    code, is_valid = result
                    results[code] = is_valid

        elif investment_type == InvestmentType.FUND:
            # Validate fund codes with East Money
            sem = asyncio.Semaphore(10)

            async def validate_single(code: str) -> tuple[str, bool]:
                async with sem:
                    return code, await self.eastmoney_client.validate_fund_code(code)

            tasks = [validate_single(code) for code in codes]
            completed = await asyncio.gather(*tasks, return_exceptions=True)

            for result in completed:
                if isinstance(result, tuple):
                    code, is_valid = result
                    results[code] = is_valid

        return results

    async def get_single_price(
        self, code: str, target_date: date, investment_type: InvestmentType
    ) -> PriceData | None:
        """Fetch a single price for a specific code and date."""
        try:
            if investment_type == InvestmentType.STOCK:
                if not self.tushare_client:
                    return None
                return await self.tushare_client.fetch_stock_price(code, target_date)

            elif investment_type == InvestmentType.FUND:
                # Fetch NAV and convert to PriceData
                nav_data = await self.eastmoney_client.fetch_fund_nav(code, target_date)
                return PriceData(
                    code=nav_data.code,
                    price_date=nav_data.nav_date,
                    price_value=nav_data.nav,
                    source="eastmoney",
                )
        except Exception as e:
            print(f"Warning: Failed to fetch price for {code}: {e}")
            return None

    def close(self) -> None:
        """Close all clients."""
        if self.tushare_client:
            self.tushare_client.close()
        if self.eastmoney_client:
            self.eastmoney_client.close()

    async def __aenter__(self) -> "PriceFetcher":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        self.close()

    def get_status(self) -> dict[str, bool]:
        """Get status of available data sources."""
        return {
            "tushare_available": bool(self.tushare_client),
            "eastmoney_available": True,  # Always available
            "stocks_available": self.is_available(InvestmentType.STOCK),
            "funds_available": self.is_available(InvestmentType.FUND),
        }
