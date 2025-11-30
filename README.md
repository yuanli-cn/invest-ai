# Invest AI - Investment Profit & Loss Calculator

A Python CLI tool for calculating investment profit and loss for Chinese stocks and mutual funds with precision cost allocation and comprehensive performance reporting.

## Features

- **FIFO Cost Allocation**: Accurate cost basis calculation using First-In-First-Out method
- **Flexible Analysis**: Support for annual returns and full investment history
- **Market Integration**: Real-time market data from Tushare (stocks) and East Money (funds)
- **Comprehensive Reports**: Detailed P&L analysis with performance metrics
- **CLI Interface**: Simple command-line interface for easy automation

## Quick Start

### Prerequisites

- Python 3.12
- uv package manager
- Tushare Pro API token for stock data
- YAML transaction file

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd invest-ai
```

2. Install dependencies with uv
```bash
uv sync
```

3. Set up your Tushare token (choose one method)

**Option A: Environment variable**
```bash
export TUSHARE_TOKEN=your_token_here
```

**Option B: Create `.env` file**
```bash
echo 'TUSHARE_TOKEN=your_token_here' > .env
```

### Usage

#### Basic usage examples:

**Show help:**
```bash
uv run python -m invest_ai.cli.main
```

**Calculate annual returns for all stocks in 2023 (using default data/stock.yaml):**
```bash
uv run python -m invest_ai.cli.main --type stock --year 2023
```

**Calculate complete history for a specific stock:**
```bash
uv run python -m invest_ai.cli.main --type stock --code 000001
```

**Calculate annual returns for all funds:**
```bash
uv run python -m invest_ai.cli.main --type fund --year 2023
```

**Full history with custom data file:**
```bash
uv run python -m invest_ai.cli.main --type stock --data my_transactions.yaml
```

## Transaction Data Format

Create a YAML file with your investment transactions:

```yaml
transactions:
  # Stock purchase
  - code: "000001"
    date: "2023-01-15"
    type: buy
    quantity: 1000
    unit_price: 25.50
    total_amount: 25500

  # Stock sale
  - code: "000001"
    date: "2023-06-20"
    type: sell
    quantity: 500
    unit_price: 28.75
    total_amount: 14375

  # Cash dividend
  - code: "000001"
    date: "2023-03-15"
    type: dividend
    quantity: 0
    unit_price: 0
    total_amount: 500
```

**Default data file paths:**
- Stock: `data/stock.yaml`
- Fund: `data/fund.yaml`

### Supported Transaction Types

| Type | Required Fields | Description |
|------|-----------------|-------------|
| **Buy** | `code`, `date`, `quantity`, `unit_price`, `total_amount` | Stock/fund purchase |
| **Sell** | `code`, `date`, `quantity`, `unit_price`, `total_amount` | Stock/fund sale |
| **Dividend** | `code`, `date`, `dividend_type`, `amount_per_share`, `total_amount` | Cash or stock dividends |

## Output Examples

### Annual Return Report
```
┌─────────────────────────────────────┐
│ PORTFOLIO - 2024
├─────────────────────────────────────┤
│ Start Value:       ¥303,686.00
│ End Value:         ¥262,858.00
│ Dividends:         ¥15,127.32
│ Capital Gain:      ¥128,393.13
│ Total Gain/Loss:   ¥210,696.96
│ Return Rate:       69.38%
└─────────────────────────────────────┘
```

The annual report shows:
- **Start Value**: Portfolio market value at year start (using actual market prices)
- **End Value**: Portfolio market value at year end (using actual market prices)
- **Dividends**: Total dividend income received during the year
- **Capital Gain**: Realized gains from selling investments
- **Return Rate**: Annual return based on (net_gain / start_value + new_investments)

### Complete History Report
```
┌─────────────────────────────────────┐
│ PORTFOLIO HISTORY
├─────────────────────────────────────┤
│ Total Invested:    ¥1,152,334.13
│ Current Value:     ¥87,027.00
│ Total P&L:         ¥164,109.87
│ Return Rate:       14.24%
└─────────────────────────────────────┘
```

## Command Reference

```
usage: invest-ai [-h] --type {stock,fund} [--code CODE] [--year YEAR] [--data DATA] [--format {table,json}]

Calculate investment profit and loss for Chinese stocks and mutual funds

options:
  -h, --help            show this help message and exit
  --type {stock,fund}   Investment type (required)
  --code CODE           Specific investment code (6-digit number)
  --year YEAR           Year for annual calculation (omit for full history)
  --data DATA           YAML transaction file (default: data/<type>.yaml)
  --format {table,json} Output format (default: table)
  --verbose             Enable verbose output
  --version             Show version
```

## Dependencies

### Python Packages
- `pydantic`: Data validation and settings management
- `pyyaml`: YAML file parsing
- `requests`: HTTP client for API calls
- `rich`: Terminal formatting and tables

### External APIs
- **Tushare Pro**: Chinese stock market data (requires API token)
- **East Money**: Chinese mutual fund NAV data (free)

## Documentation

This project follows a structured documentation approach:

### Design Documents
- **[Design Specification](docs/design.md)**: User workflows, system architecture, and component interactions

### Domain Knowledge
- **[Stock Price Retrieval](docs/domain-knowledge/stock-price-retrieval.md)**: Tushare API usage and verification
- **[Fund NAV Retrieval](docs/domain-knowledge/fund-nav-retrieval.md)**: East Money API integration patterns
- **[Investment Calculation Methods](docs/domain-knowledge/investment-calculation-methods.md)**: FIFO cost allocation and performance metrics

### Project Guidelines
- **[CLAUDE.md](CLAUDE.md)**: Project-specific development guidelines and documentation standards

## API Configuration

### Tushare Pro Setup
1. Register at [Tushare Pro](https://tushare.pro/)
2. Get your API token
3. Set environment variable: `export TUSHARE_TOKEN=your_token_here`

### API Rate Limits
- **Tushare**: 200 calls/day for free tier
- **East Money**: No authentication required

## Development

### Running Tests

**Run all tests:**
```bash
uv run pytest
```

**Run only unit tests:**
```bash
uv run pytest tests/unit/
```

**Run only integration tests:**
```bash
uv run pytest tests/integration/
```

**Run specific test file:**
```bash
uv run pytest tests/integration/test_all_user_scenarios.py -v
```

### Test Coverage

This project maintains **100% test pass rate** with **74% code coverage**:

#### Test Summary: 444 tests passing
- FIFO cost basis calculations
- Annual return calculations  
- Complete history calculations
- Transaction validation and filtering
- CLI argument handling
- API client integration
- Report generation

#### Integration Tests
Comprehensive end-to-end tests covering all user scenarios:

- **Stock Annual Returns**: Specific stock and portfolio calculations
- **Stock Complete History**: Full investment history for specific stocks and portfolios
- **Fund Annual Returns**: Specific fund and portfolio calculations
- **Fund Complete History**: Full investment history for specific funds and portfolios
- **Mixed Portfolio**: Combined stock and fund portfolio calculations
- **JSON Output Format**: Structured data output verification
- **Error Handling**: Invalid codes, files, and edge cases
- **Dividend Tracking**: Separate dividend income tracking
- **FIFO Accuracy**: Cost basis calculation verification

### Code Formatting
```bash
uv run black .
uv run ruff check .
```

### Project Structure
```
invest-ai/
├── main.py                 # CLI entry point
├── src/                    # Source modules
├── tests/                  # Test suite
├── docs/                   # Documentation
├── pyproject.toml          # Project configuration
├── CLAUDE.md              # Development guidelines
└── README.md              # This file
```

## Performance Considerations

- **Memory Efficient**: Processes transactions in chronological order
- **API Rate Limiting**: Tushare API has 50 requests/minute limit; built-in rate limiter prevents exceeding this
- **API Optimization**: Fetches only required data points for year-start and year-end prices
- **Error Handling**: Graceful degradation when external APIs are unavailable

## GitHub Actions (Automated Daily Reports)

The project includes a GitHub Actions workflow that runs daily (Mon-Fri at 23:00 Beijing Time) and sends reports to Telegram.

### Required GitHub Secrets

Configure this secret in your repository settings (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `TUSHARE_TOKEN` | Tushare Pro API token for stock data |

Note: Telegram Bot token and Chat ID are pre-configured in the workflow.

### Telegram Message Format

Reports are sent in a clean format:
```
📈 Stock Portfolio 2024
Start: ¥303,686
End: ¥262,858
Dividends: ¥15,127
Gain: ¥210,697
Return: 69.4%
```

### Manual Trigger

You can manually trigger the workflow from the GitHub Actions tab.

## Contributing

Follow the guidelines in [CLAUDE.md](CLAUDE.md) for:

1. Code style and formatting standards
2. Documentation requirements
3. Testing strategies
4. Implementation principles

## License

[Add your license information here]

## Support

For issues and questions:

1. Check the [documentation](docs/) for detailed information
2. Review the [development guidelines](CLAUDE.md)
3. Ensure all external dependencies are properly configured