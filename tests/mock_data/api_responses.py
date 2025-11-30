"""Mock API responses for integration testing."""

from typing import Any


class MockTushareResponses:
    """Mock Tushare API responses for stock data."""

    @staticmethod
    def get_stock_daily_response(
        ts_code: str, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """Get mock stock daily data response."""
        # Realistic price data for different stocks
        price_data = {
            "00700": {
                "items": [
                    {
                        "trade_date": "20231201",
                        "close": 420.50,
                        "open": 418.00,
                        "high": 422.00,
                        "low": 416.50,
                    },
                    {
                        "trade_date": "20231130",
                        "close": 418.20,
                        "open": 419.00,
                        "high": 421.50,
                        "low": 417.00,
                    },
                    {
                        "trade_date": "20231031",
                        "close": 395.80,
                        "open": 398.00,
                        "high": 400.50,
                        "low": 394.00,
                    },
                ]
            },
            "09988": {
                "items": [
                    {
                        "trade_date": "20231201",
                        "close": 75.20,
                        "open": 74.50,
                        "high": 76.00,
                        "low": 73.80,
                    },
                    {
                        "trade_date": "20231130",
                        "close": 74.30,
                        "open": 75.00,
                        "high": 75.50,
                        "low": 73.50,
                    },
                    {
                        "trade_date": "20231031",
                        "close": 68.40,
                        "open": 69.00,
                        "high": 70.00,
                        "low": 67.50,
                    },
                ]
            },
            "600519": {
                "items": [
                    {
                        "trade_date": "20231201",
                        "close": 1685.00,
                        "open": 1680.00,
                        "high": 1690.00,
                        "low": 1675.00,
                    },
                    {
                        "trade_date": "20231130",
                        "close": 1682.50,
                        "open": 1685.00,
                        "high": 1688.00,
                        "low": 1680.00,
                    },
                    {
                        "trade_date": "20231031",
                        "close": 1650.00,
                        "open": 1655.00,
                        "high": 1660.00,
                        "low": 1645.00,
                    },
                ]
            },
            "601398": {
                "items": [
                    {
                        "trade_date": "20231201",
                        "close": 5.18,
                        "open": 5.15,
                        "high": 5.20,
                        "low": 5.12,
                    },
                    {
                        "trade_date": "20231130",
                        "close": 5.16,
                        "open": 5.18,
                        "high": 5.20,
                        "low": 5.14,
                    },
                    {
                        "trade_date": "20231031",
                        "close": 4.85,
                        "open": 4.88,
                        "high": 4.92,
                        "low": 4.82,
                    },
                ]
            },
        }

        default_response = {
            "items": [
                {
                    "trade_date": "20231201",
                    "close": 100.00,
                    "open": 99.50,
                    "high": 100.50,
                    "low": 99.00,
                },
                {
                    "trade_date": "20231130",
                    "close": 99.50,
                    "open": 100.00,
                    "high": 100.25,
                    "low": 99.25,
                },
                {
                    "trade_date": "20231031",
                    "close": 98.75,
                    "open": 99.50,
                    "high": 99.75,
                    "low": 98.50,
                },
            ]
        }

        return {
            "request_id": "123456789",
            "code": 0,
            "msg": None,
            "data": price_data.get(ts_code, default_response),
        }

    @staticmethod
    def get_stock_basic_info(ts_code: str) -> dict[str, Any]:
        """Get mock stock basic info response."""
        stock_info = {
            "00700": {"name": "腾讯控股", "industry": "软件服务", "market": "HK"},
            "09988": {"name": "阿里巴巴-SW", "industry": "互联网", "market": "HK"},
            "600519": {"name": "贵州茅台", "industry": "白酒", "market": "主板"},
            "601398": {"name": "工商银行", "industry": "银行", "market": "主板"},
        }

        return {
            "request_id": "123456789",
            "code": 0,
            "msg": None,
            "data": [
                stock_info.get(
                    ts_code,
                    {"name": "Unknown", "industry": "Unknown", "market": "Unknown"},
                )
            ],
        }


class MockEastMoneyResponses:
    """Mock East Money API responses for fund NAV data."""

    @staticmethod
    def get_fund_nav_response(fund_code: str) -> dict[str, Any]:
        """Get mock fund NAV response."""
        nav_data = {
            "110022": {
                "datas": [
                    {"FSRQ": "2023-12-01", "NAV": 3.12, "AccumulativeNAV": 1.2345},
                    {"FSRQ": "2023-11-30", "NAV": 3.08, "AccumulativeNAV": 1.2167},
                    {"FSRQ": "2023-10-31", "NAV": 2.95, "AccumulativeNAV": 1.1876},
                ]
            },
            "110020": {
                "datas": [
                    {"FSRQ": "2023-12-01", "NAV": 4.8621, "AccumulativeNAV": 1.5847},
                    {"FSRQ": "2023-11-30", "NAV": 4.8452, "AccumulativeNAV": 1.5789},
                    {"FSRQ": "2023-10-31", "NAV": 4.7823, "AccumulativeNAV": 1.5547},
                ]
            },
            "160106": {
                "datas": [
                    {"FSRQ": "2023-12-01", "NAV": 3.1875, "AccumulativeNAV": 2.3421},
                    {"FSRQ": "2023-11-30", "NAV": 3.1652, "AccumulativeNAV": 2.3287},
                    {"FSRQ": "2023-10-31", "NAV": 3.0987, "AccumulativeNAV": 2.2793},
                ]
            },
        }

        default_response = {
            "datas": [
                {"FSRQ": "2023-12-01", "NAV": 1.0000, " AccumulativeNAV": 1.0000},
                {"FSRQ": "2023-11-30", "NAV": 0.9950, " AccumulativeNAV": 0.9950},
                {"FSRQ": "2023-10-31", "NAV": 0.9875, " AccumulativeNAV": 0.9875},
            ]
        }

        return {
            "rc": 0,
            "rt": 6,
            "svrid": "123456",
            "lt": 1,
            "full": 1,
            "dlmt": 0,
            "data": nav_data.get(fund_code, default_response),
        }

    @staticmethod
    def get_fund_info_response(fund_code: str) -> dict[str, Any]:
        """Get mock fund info response."""
        fund_info = {
            "110022": {
                "NAME": "易方达上证50指数",
                "FUNDTYPE": "指数型",
                "ESTABDATE": "2004-03-22",
            },
            "110020": {
                "NAME": "易方达沪深300指数",
                "FUNDTYPE": "指数型",
                "ESTABDATE": "2012-03-06",
            },
            "160106": {
                "NAME": "南方成长混合",
                "FUNDTYPE": "混合型",
                "ESTABDATE": "2004-01-09",
            },
        }

        return {
            "rc": 0,
            "rt": 6,
            "svrid": "123456",
            "lt": 1,
            "full": 1,
            "dlmt": 0,
            "data": {
                "DATAS": fund_info.get(
                    fund_code, {"NAME": "Unknown", "FUNDTYPE": "Unknown"}
                )
            },
        }


class MockIntegrationTestData:
    """Complete integration test scenarios with expected results."""

    @staticmethod
    def get_scenario_data() -> dict[str, Any]:
        """Get complete test scenarios with inputs and expected outputs."""
        return {
            "scenario_1_stock_analysis": {
                "description": "Stock annual return analysis",
                "command_args": [
                    "--type",
                    "stock",
                    "--data",
                    "tests/data/integration_portfolio.yaml",
                    "--code",
                    "000001",
                    "--year",
                    "2023",
                ],
                "mock_apis": {
                    "tushare": {
                        "daily": MockTushareResponses.get_stock_daily_response(
                            "00700", "20230101", "20231231"
                        ),
                        "basic": MockTushareResponses.get_stock_basic_info("00700"),
                    }
                },
                "expected_output": {
                    "investment_type": "stock",
                    "year": 2023,
                    "code": "00700",
                    "investments": [
                        {
                            "code": "00700",
                            "total_invested": 251000.0,  # 175000 + 76000
                            "realized_gain": 46875.0,  # (420-350)*300 - (420-380)*0 = 21000
                            "unrealized_gain": 33825.0,  # 400*420.50 - 400*350 (remaining)
                            "total_gain": 80700.0,
                            "return_rate": 32.15,  # 80700 / 251000 * 100
                            "current_value": 157425.0,  # 400 * 420.50 (remaining shares) + 126000 (sold)
                            "cost_basis": 134475.0,
                        }
                    ],
                },
            },
            "scenario_2_mixed_portfolio_history": {
                "description": "Mixed portfolio complete history analysis",
                "command_args": [
                    "--type",
                    "stock",
                    "--data",
                    "tests/data/integration_portfolio.yaml",
                    "--code",
                    "000001",
                ],
                "mock_apis": {
                    "tushare": {
                        "daily": MockTushareResponses.get_stock_daily_response(
                            "000001", "20220101", "20231231"
                        ),
                        "basic": MockTushareResponses.get_stock_basic_info("000001"),
                    }
                },
                "expected_output": {
                    "investment_type": "stock",
                    "code": "000001",
                    "total_invested": 12500.0,
                    "current_value": 33600.0,  # 2000 remaining * 16.80 (current price)
                    "total_gain": 16180.0,  # dividends + realized profit
                    "return_rate": 129.44,  # 16180 / 12500 * 100
                },
            },
            "scenario_3_fund_annual_analysis": {
                "description": "E Fund CSI 300 annual analysis",
                "command_args": [
                    "--type",
                    "fund",
                    "--data",
                    "realistic_portfolio.yaml",
                    "--code",
                    "110020",
                    "--year",
                    "2023",
                ],
                "mock_apis": {
                    "eastmoney": {
                        "nav": MockEastMoneyResponses.get_fund_nav_response("110020"),
                        "info": MockEastMoneyResponses.get_fund_info_response("110020"),
                    }
                },
                "expected_output": {
                    "investment_type": "fund",
                    "year": 2023,
                    "code": "110020",
                    "start_value": 102570.0,  # 45000 + 21750 + 23100 + 20750
                    "end_value": 62880.0,  # (7000+5000+5000) * 4.8621
                    "net_gain": -39870.0,
                    "dividends": 1850.0,
                    "return_rate": -38.86,
                },
            },
            "scenario_4_portfolio_valuation": {
                "description": "Complete portfolio current valuation",
                "command_args": [
                    "--type",
                    "stock",
                    "--data",
                    "realistic_portfolio.yaml",
                ],
                "mock_apis": {
                    "tushare": {
                        "daily": {
                            "00700": MockTushareResponses.get_stock_daily_response(
                                "00700", "20220101", "20231231"
                            ),
                            "09988": MockTushareResponses.get_stock_daily_response(
                                "09988", "20220101", "20231231"
                            ),
                            "600519": MockTushareResponses.get_stock_daily_response(
                                "600519", "20220101", "20231231"
                            ),
                            "601398": MockTushareResponses.get_stock_daily_response(
                                "601398", "20220101", "20231231"
                            ),
                        },
                        "basic": {
                            "00700": MockTushareResponses.get_stock_basic_info("00700"),
                            "09988": MockTushareResponses.get_stock_basic_info("09988"),
                            "600519": MockTushareResponses.get_stock_basic_info(
                                "600519"
                            ),
                            "601398": MockTushareResponses.get_stock_basic_info(
                                "601398"
                            ),
                        },
                    },
                    "eastmoney": {
                        "nav": {
                            "110020": MockEastMoneyResponses.get_fund_nav_response(
                                "110020"
                            ),
                            "160106": MockEastMoneyResponses.get_fund_nav_response(
                                "160106"
                            ),
                        },
                        "info": {
                            "110020": MockEastMoneyResponses.get_fund_info_response(
                                "110020"
                            ),
                            "160106": MockEastMoneyResponses.get_fund_info_response(
                                "160106"
                            ),
                        },
                    },
                },
                "expected_portfolio_value": {
                    "total_aum": 724025.0,  # Realistic portfolio valuation
                    "breakdown": {
                        "stocks": 550625.0,  # 00700 + 09988 + 600519 + 601398
                        "funds": 159240.0,  # 110020 + 160106
                        "bonds": 490000.0,  # 010107
                        "international": 74160.0,  # TSLA
                    },
                },
            },
        }
