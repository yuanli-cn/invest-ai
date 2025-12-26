"""Tushare stock market data client."""

import asyncio
from datetime import date, timedelta

import requests

from invest_ai.config import create_api_config
from invest_ai.models import PriceData


class TushareClient:
    """Tushare Pro API client for Chinese stock market data."""

    # Rate limit retry settings
    _RATE_LIMIT_WAIT = 61  # Wait 61 seconds when rate limited (API limit is per minute)

    def __init__(self, token: str | None = None):
        """Initialize the Tushare client."""
        self.config = create_api_config()
        self.session = requests.Session()

        # Override token if provided
        if token:
            self.config.tushare.token = token

        if not self.config.tushare.is_configured:
            raise ValueError(
                "Tushare token is required. Set TUSHARE_TOKEN environment variable."
            )

    async def fetch_stock_price(self, code: str, target_date: date) -> PriceData:
        """Fetch stock price for a specific code and date."""
        # Convert to Tushare format (6-digit code + .SZ or .SH)
        ts_code = self._convert_to_tushare_code(code)

        # Try target date first, then adjust for trading days
        trading_date = await self._get_trading_date(ts_code, target_date)

        # Try fetching data with fallback to previous trading days if no data
        max_fallback_days = 7  # Max 7 days of fallback
        last_error = None

        for days_back in range(max_fallback_days + 1):
            check_date = target_date - timedelta(days=days_back)

            # Verify it's a trading day before making API call
            actual_trading_date = await self._get_trading_date(ts_code, check_date)
            if actual_trading_date != check_date:
                continue  # Skip non-trading days

            request_data = {
                "api_name": "daily",
                "token": self.config.tushare.token,
                "params": {
                    "ts_code": ts_code,
                    "trade_date": actual_trading_date.strftime("%Y%m%d"),
                    "fields": "ts_code,trade_date,close,high,low,open,pre_close",
                    "limit": 1,
                },
            }

            try:
                response = await self._make_api_request(request_data)
                if not response or "data" not in response or not response["data"]:
                    last_error = ValueError(f"No data found for {code} on {actual_trading_date}")
                    continue

                # Parse response - Tushare returns {fields: [...], items: [[...]]}
                data = response["data"]
                if isinstance(data, dict) and "items" in data and "fields" in data:
                    items = data["items"]
                    fields = data["fields"]
                    if items and len(items) > 0:
                        # Convert items list to dict using fields
                        item_dict = dict(zip(fields, items[0]))
                        price = float(item_dict.get("close", 0))
                        if price <= 0:
                            last_error = ValueError(f"Invalid price data for {code}: {item_dict}")
                            continue

                        # Success! Return price data
                        if days_back > 0:
                            print(
                                f"Info: Using price from {actual_trading_date} "
                                f"({days_back} day{'s' if days_back > 1 else ''} earlier) "
                                f"for {code} on {target_date}"
                            )

                        return PriceData(
                            code=code, price_date=actual_trading_date, price_value=price, source="tushare"
                        )
                    else:
                        # Empty items array - try next day
                        last_error = ValueError(f"No items in response for {code} on {actual_trading_date}")
                        continue
                else:
                    last_error = ValueError(f"Unexpected response format: {data}")
                    continue

            except Exception as e:
                last_error = e
                continue  # Try previous day

        # If we get here, no data was found
        raise RuntimeError(
            f"Error fetching stock price for {code} on {target_date}: "
            f"No data available for the target date or previous {max_fallback_days} trading days"
        ) from last_error

    async def fetch_current_prices(self, codes: list[str]) -> dict[str, PriceData]:
        """Fetch current prices for multiple stock codes."""
        results = {}

        # Process in parallel with limited concurrency
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests

        async def fetch_single(code: str) -> tuple[str, PriceData | None]:
            async with semaphore:
                try:
                    # Get price for today (or most recent trading day)
                    today = date.today()
                    price_data = await self.fetch_stock_price(code, today)
                    return code, price_data
                except Exception as e:
                    print(f"Warning: Failed to fetch price for {code}: {e}")
                    return code, None

        tasks = [fetch_single(code) for code in codes]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if isinstance(result, tuple):
                code, price_data = result
                if price_data:
                    results[code] = price_data

        return results

    async def fetch_historical_prices(
        self, codes: list[str], dates: list[date]
    ) -> dict[str, list[PriceData]]:
        """Fetch historical prices for multiple codes and dates."""
        results = {}

        for code in codes:
            code_results = []
            for target_date in dates:
                try:
                    price_data = await self.fetch_stock_price(code, target_date)
                    code_results.append(price_data)
                except Exception as e:
                    print(
                        f"Warning: Failed to fetch historical price for {code} on {target_date}: {e}"
                    )
                    # Continue with other dates
                    continue
            results[code] = code_results

        return results

    def _convert_to_tushare_code(self, code: str) -> str:
        """Convert 6-digit code to Tushare format with exchange suffix."""
        code = code.zfill(6)

        # Shanghai Stock Exchange (starts with 6)
        if code.startswith("6"):
            return f"{code}.SH"

        # Shenzhen Stock Exchange (starts with 0, 3)
        elif code.startswith(("0", "3", "2")):
            return f"{code}.SZ"

        # Beijing Stock Exchange (starts with 8, 4)
        elif code.startswith(("8", "4")):
            return f"{code}.BJ"

        else:
            # Default to Shenzhen for unknown patterns
            return f"{code}.SZ"

    async def _get_trading_date(self, ts_code: str, target_date: date) -> date:
        """Get the nearest trading date to the target date.
        
        Uses local trading calendar to avoid API calls.
        """
        from .trading_days import TradingDaysChina
        
        calendar = TradingDaysChina()
        
        # First try the target date
        if calendar.is_trading_day(target_date):
            return target_date

        # Try previous days up to 10 days (to handle long holidays)
        for days_back in range(1, 11):
            test_date = target_date - timedelta(days=days_back)
            if calendar.is_trading_day(test_date):
                return test_date

        # If no trading day found, return target date anyway
        return target_date

    async def _make_api_request(self, request_data: dict) -> dict[str, object]:
        """Make an API request with retry logic and rate limit handling."""
        headers = self.config.get_headers("tushare")
        url = self.config.tushare.base_url
        max_rate_limit_retries = 3  # Max times to retry on rate limit

        for attempt in range(self.config.tushare.retry_count + 1):
            try:
                response = self.session.post(
                    url,
                    json=request_data,
                    headers=headers,
                    timeout=self.config.tushare.timeout,
                )
                response.raise_for_status()

                data: dict[str, object] = response.json()
                if data.get("code") != 0:
                    error_msg = str(data.get("msg", "Unknown error"))
                    
                    # Check if it's a rate limit error
                    if "每分钟最多访问" in error_msg or "rate limit" in error_msg.lower():
                        if attempt < max_rate_limit_retries:
                            print(f"Rate limit hit, waiting {self._RATE_LIMIT_WAIT}s before retry...")
                            await asyncio.sleep(self._RATE_LIMIT_WAIT)
                            continue
                    
                    raise ValueError(f"Tushare API error: {error_msg}")

                return data

            except requests.exceptions.RequestException:
                if attempt < self.config.tushare.retry_count:
                    await asyncio.sleep(self.config.tushare.retry_delay * (2**attempt))
                    continue
                raise

        raise RuntimeError(f"Failed after {self.config.tushare.retry_count} retries")

    async def validate_code(self, code: str) -> bool:
        """Validate if a stock code exists and is tradeable."""
        try:
            # Try to fetch recent data
            ts_code = self._convert_to_tushare_code(code)
            today = date.today()
            await self._get_trading_date(ts_code, today)
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Close the session."""
        if self.session:
            self.session.close()

    async def __aenter__(self) -> "TushareClient":
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
