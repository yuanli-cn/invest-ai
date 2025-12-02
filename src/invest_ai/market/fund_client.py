"""East Money mutual fund NAV data client."""

import asyncio
from datetime import date, timedelta

import requests

from invest_ai.config import create_api_config
from invest_ai.models import NavData, PriceData


class EastMoneyClient:
    """East Money API client for Chinese mutual fund NAV data."""

    def __init__(self) -> None:
        """Initialize the East Money client."""
        self.config = create_api_config()
        self.session = requests.Session()

    async def fetch_fund_nav(self, code: str, target_date: date) -> NavData:
        """Fetch fund NAV for a specific code and date."""
        from .trading_days import TradingDaysChina
        
        # Adjust to nearest trading day to avoid unnecessary API calls
        calendar = TradingDaysChina()
        trading_date = target_date
        if not calendar.is_trading_day(target_date):
            trading_date = calendar.get_previous_trading_day(target_date, max_days_back=10)
        
        # Format parameters according to East Money API requirements
        fund_code = code.zfill(6)
        begin_date = trading_date.strftime("%Y-%m-%d")
        end_date = trading_date.strftime("%Y-%m-%d")

        # East Money requires both date filtering AND pagination
        url = (
            f"{self.config.eastmoney.base_url}/f10/lsjz"
            f"?fundCode={fund_code}"
            f"&beginDate={begin_date}"
            f"&endDate={end_date}"
            f"&pageIndex=1"
            f"&pageSize=1"
        )

        headers = self.config.get_headers("eastmoney")

        try:
            response = await self._make_api_request(url, headers)

            if not response:
                raise ValueError(f"No data found for fund {code} on {target_date}")

            # Parse JSON response directly (no callback wrapper)
            data = response

            # Check if data is valid
            if not data or "Data" not in data or not data["Data"]:
                raise ValueError(f"No NAV data found for fund {code} on {target_date}")

            nav_data = data["Data"]
            
            # Handle different response formats
            # Format 1: Data is a dict with LSJZList containing the items
            # Format 2: Data is a direct list of items
            items = None
            if isinstance(nav_data, dict) and "LSJZList" in nav_data:
                items = nav_data["LSJZList"]
            elif isinstance(nav_data, list):
                items = nav_data
            
            if items and len(items) > 0:
                item = items[0]

                # Parse NAV fields
                nav_value = float(item.get("DWJZ", "0"))  # 单位净值 (unit NAV)
                accumulated_nav = float(
                    item.get("LJJZ", "0")
                )  # 累计净值 (accumulated NAV)

                if nav_value <= 0:
                    raise ValueError(f"Invalid NAV data for fund {code}: {item}")

                return NavData(
                    code=fund_code,
                    nav_date=trading_date,
                    nav=nav_value,
                    accumulated_nav=accumulated_nav if accumulated_nav > 0 else None,
                )
            else:
                raise ValueError(f"Unexpected response format: {data}")

        except Exception as e:
            raise RuntimeError(
                f"Error fetching fund NAV for {code} on {target_date}: {e}"
            ) from e

    async def fetch_current_navs(self, codes: list[str]) -> dict[str, NavData]:
        """Fetch current NAVs for multiple fund codes."""
        results: dict[str, NavData] = {}

        # Process in parallel with limited concurrency
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests

        async def fetch_single(code: str) -> tuple[str, NavData | None]:
            async with semaphore:
                try:
                    # Get NAV for today (or most recent trading day)
                    today = date.today()
                    nav_data = await self.fetch_fund_nav(code, today)
                    return code, nav_data
                except Exception as e:
                    print(f"Warning: Failed to fetch NAV for {code}: {e}")
                    return code, None

        tasks = [fetch_single(code) for code in codes]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if isinstance(result, tuple):
                code, nav_data = result
                if nav_data:
                    results[code] = nav_data

        return results

    async def fetch_historical_navs(
        self, codes: list[str], dates: list[date]
    ) -> dict[str, list[NavData]]:
        """Fetch historical NAVs for multiple codes and dates."""
        results = {}

        for code in codes:
            code_results = []
            for target_date in dates:
                try:
                    nav_data = await self.fetch_fund_nav(code, target_date)
                    code_results.append(nav_data)
                except Exception as e:
                    print(
                        f"Warning: Failed to fetch historical NAV for {code} on {target_date}: {e}"
                    )
                    # Continue with other dates
                    continue
            results[code] = code_results

        return results

    async def fetch_fund_prices_as_nav(
        self, codes: list[str], dates: list[date]
    ) -> dict[str, list[PriceData]]:
        """Fetch fund NAVs and convert them to PriceData format for consistency."""
        nav_results = await self.fetch_historical_navs(codes, dates)
        price_results = {}

        for code, nav_data_list in nav_results.items():
            price_data_list = []
            for nav_data in nav_data_list:
                # Convert NavData to PriceData (use NAV as price)
                price_data = PriceData(
                    code=nav_data.code,
                    price_date=nav_data.nav_date,
                    price_value=nav_data.nav,  # Use NAV as the "price"
                    source=nav_data.source,
                )
                price_data_list.append(price_data)
            price_results[code] = price_data_list

        return price_results

    async def fetch_current_prices_as_nav(
        self, codes: list[str]
    ) -> dict[str, PriceData]:
        """Fetch current NAVs and convert them to PriceData format."""
        nav_results = await self.fetch_current_navs(codes)
        price_results = {}

        for code, nav_data in nav_results.items():
            # Convert NavData to PriceData
            price_data = PriceData(
                code=nav_data.code,
                price_date=nav_data.nav_date,
                price_value=nav_data.nav,  # Use NAV as the "price"
                source=nav_data.source,
            )
            price_results[code] = price_data

        return price_results

    async def validate_fund_code(self, code: str) -> bool:
        """Validate if a fund code exists and is active."""
        try:
            # Try to fetch recent NAV data
            fund_code = code.zfill(6)
            today = date.today() - timedelta(
                days=1
            )  # Use yesterday to avoid timing issues

            url = (
                f"{self.config.eastmoney.base_url}/f10/lsjz"
                f"?fundCode={fund_code}"
                f"&beginDate={today.strftime('%Y-%m-%d')}"
                f"&endDate={today.strftime('%Y-%m-%d')}"
                f"&pageIndex=1"
                f"&pageSize=1"
            )

            headers = self.config.get_headers("eastmoney")
            response = await self._make_api_request(url, headers)

            if response:
                data = response
                return bool(data and "Data" in data and data["Data"])
            return False

        except Exception:
            return False

    async def _make_api_request(
        self, url: str, headers: dict
    ) -> dict[str, object] | None:
        """Make an API request with retry logic."""
        for attempt in range(self.config.eastmoney.retry_count + 1):
            try:
                response = self.session.get(
                    url, headers=headers, timeout=self.config.eastmoney.timeout
                )
                response.raise_for_status()
                data: dict[str, object] = response.json()
                return data

            except requests.exceptions.RequestException:
                if attempt < self.config.eastmoney.retry_count:
                    await asyncio.sleep(
                        self.config.eastmoney.retry_delay * (2**attempt)
                    )
                    continue
                raise

        raise RuntimeError(f"Failed after {self.config.eastmoney.retry_count} retries")

    def close(self) -> None:
        """Close the session."""
        if self.session:
            self.session.close()

    async def __aenter__(self) -> "EastMoneyClient":
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
