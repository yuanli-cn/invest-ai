# Project Context

## Status
**Version**: 1.0.0 (Initial Release)  
**Date**: 2025-11-30  
**Status**: ✅ Core features complete and tested

### Completed Capabilities
- CLI interface with argument parsing and validation
- FIFO cost basis calculation for buy/sell/dividend transactions
- Annual return calculation with year-start/end market prices
- Complete history calculation with realized/unrealized gains
- Market data integration (Tushare for stocks, EastMoney for funds)
- Report generation (table and JSON formats)
- GitHub Actions for automated daily reports via Telegram

## Purpose
A Python CLI tool for calculating investment profit and loss for Chinese stocks and mutual funds with precision cost allocation (FIFO) and comprehensive performance reporting.

## Tech Stack
- **Language**: Python 3.12
- **Package Manager**: uv
- **Data Validation**: Pydantic 2.x
- **HTTP Client**: requests
- **Configuration**: pyyaml, pydantic-settings
- **Output Formatting**: rich
- **Code Quality**: ruff, black, mypy

## Project Conventions

### Code Style
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Line length: 88 characters (black default)
- Type annotations required (mypy strict mode)

### Architecture Patterns
- **Modular Design**: Separate modules for CLI, transaction, market, calculation, reporting
- **Async/Await**: Async interfaces for API calls (using sync requests underneath for simplicity)
- **Pydantic Models**: All data structures use Pydantic for validation
- **FIFO Cost Allocation**: First-In-First-Out method for cost basis calculations
- **CLI Design**: Returns error codes (not exceptions), supports argument injection for testing

### Testing Strategy
- **Unit Tests**: Individual components in isolation (`tests/unit/`)
- **Integration Tests**: End-to-end workflows with mocked APIs (`tests/integration/`)
- **Coverage**: pytest-cov with coverage reporting
- All tests must pass before commits

### Git Workflow
- Feature branches for development
- Run `uv run pytest` before committing
- Run `uv run ruff check .` and `uv run black .` for formatting

### Development Rules
- All lint and tests must pass before any code changes
- Update OpenSpec documents before implementing code changes
- Domain knowledge (API patterns, calculation methods) is documented in specs

## Domain Context

### Investment Types
- **Stocks**: Chinese A-shares (6-digit codes starting with 0, 3, 6)
- **Funds**: Mutual funds (6-digit codes)

### Transaction Types
- **Buy**: Purchase shares/units
- **Sell**: Sell shares/units
- **Dividend**: Cash or stock dividends

### Calculation Methods
- **FIFO (First-In-First-Out)**: Oldest purchases are sold first for cost basis
- **Annual Returns**: Performance for a specific year
- **Complete History**: Full investment history from first transaction

## Important Constraints
- **Platform**: Linux only
- **No Database**: File-based storage (YAML transactions)
- **CLI Only**: No web interface
- **API Limits**: Tushare free tier has 200 calls/day

## External Dependencies

### Tushare Pro (Stock Prices)
- **Purpose**: Fetch Chinese stock market prices
- **Authentication**: Environment variable `TUSHARE_TOKEN`
- **Rate Limit**: 200 calls/day (free tier)

### East Money (Fund NAV)
- **Purpose**: Fetch mutual fund NAV data
- **Authentication**: None required
- **Rate Limit**: No explicit limit
