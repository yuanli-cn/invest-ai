# Invest AI

A CLI tool for calculating investment profit and loss for Chinese stocks and mutual funds.

> 🤖 **This project is 100% AI-generated** using [Windsurf](https://codeium.com/windsurf) with Claude as the AI assistant.

## Features

- **FIFO Cost Basis**: First-In-First-Out cost allocation for accurate gain/loss calculation
- **Annual Reports**: Year-over-year performance with market prices at year boundaries
- **History Reports**: Complete investment history from first transaction
- **Market Data**: Tushare (stocks) and East Money (funds) integration
- **Automated Reports**: GitHub Actions workflow for daily Telegram notifications

## Installation

```bash
# Clone and install
git clone https://github.com/your-username/invest-ai.git
cd invest-ai
uv sync

# Set Tushare token
export TUSHARE_TOKEN=your_token_here
# Or create .env file
echo 'TUSHARE_TOKEN=your_token_here' > .env
```

## Usage

### Annual Returns

```bash
# Stock portfolio for current year
uv run python -m invest_ai.cli.main --type stock --year 2025

# Fund portfolio for specific year
uv run python -m invest_ai.cli.main --type fund --year 2024

# Specific stock
uv run python -m invest_ai.cli.main --type stock --code 000001 --year 2024
```

### Complete History

```bash
# All stocks
uv run python -m invest_ai.cli.main --type stock

# Specific fund
uv run python -m invest_ai.cli.main --type fund --code 050027

# Custom data file
uv run python -m invest_ai.cli.main --type fund --data my_portfolio.yaml
```

### Output Formats

```bash
# Table format (default)
uv run python -m invest_ai.cli.main --type stock --year 2025

# JSON format (for automation)
uv run python -m invest_ai.cli.main --type stock --year 2025 --format json
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

### Specifications (OpenSpec)

This project uses [OpenSpec](https://github.com/openspec) for spec-driven development:

| Spec | Description |
|------|-------------|
| [cli](openspec/specs/cli/spec.md) | Command-line interface requirements |
| [investment-calculation](openspec/specs/investment-calculation/spec.md) | FIFO, annual, and history calculation logic |
| [market-data](openspec/specs/market-data/spec.md) | Tushare and East Money API integration |
| [reporting](openspec/specs/reporting/spec.md) | Output formatting and report generation |
| [transaction-processing](openspec/specs/transaction-processing/spec.md) | Transaction loading and validation |

### Other Documents

- [openspec/project.md](openspec/project.md) - Project conventions and tech stack
- [tests/TESTING.md](tests/TESTING.md) - Testing strategy and guidelines

## API Configuration

### Tushare Pro Setup
1. Register at [Tushare Pro](https://tushare.pro/)
2. Get your API token
3. Set environment variable: `export TUSHARE_TOKEN=your_token_here`

### API Rate Limits
- **Tushare**: 200 calls/day for free tier
- **East Money**: No authentication required

## GitHub Actions (Automated Daily Reports)

The project includes a GitHub Actions workflow that runs daily (Mon-Fri at 23:00 Beijing Time) and sends reports to Telegram.

### Required GitHub Secrets

Configure these secrets in your repository settings (Settings → Secrets and variables → Actions → Repository secrets):

| Secret | Description |
|--------|-------------|
| `TUSHARE_TOKEN` | Tushare Pro API token |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot token |
| `TELEGRAM_CHAT_ID` | Telegram Chat/Group ID |

### Telegram Message Format

```
📈 Stock Portfolio 2025
Start: ¥261,173
End: ¥87,027
Dividends: ¥8,210
Gain: ¥14,031
Return: 5.4%
```

### Trigger Options

- **Automatic**: Mon-Fri at 23:00 Beijing Time
- **On Push**: Runs when pushing to main branch
- **Manual**: Actions tab → Run workflow

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check .
```

See [openspec/project.md](openspec/project.md) for coding conventions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.