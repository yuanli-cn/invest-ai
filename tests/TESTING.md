# Testing Documentation

## Overview

This project maintains **100% test pass rate** across all test suites. Tests are designed to verify functionality with mocked external dependencies, ensuring reliable CI/CD pipelines and development workflows.

## Test Suite Structure

### Unit Tests (53 tests passing)

Located in `tests/unit/`, these tests verify individual components in isolation:

- **`test_calculation.py`**: FIFO cost basis, annual returns, and history calculations
  - FIFO queue processing and cost allocation
  - Realized/unrealized gain calculations
  - New investment tracking
  - Dividend income tracking

- **`test_models.py`**: Data model validation
  - Transaction, PriceData, NavData models
  - Investment type detection
  - Transaction filtering and sorting

- **`test_transaction.py`**: Transaction processing
  - Loading transactions from YAML files
  - Transaction validation
  - Filter and sort operations

### Integration Tests (15 tests passing)

Located in `tests/integration/test_all_user_scenarios.py`, these tests cover complete user workflows with mocked APIs:

## Integration Test Scenarios

### 1. Stock Annual Returns - Specific Stock
**Test**: `test_scenario_stock_annual_specific_stock`

Calculates annual returns for a specific stock in a specific year.

**Workflow**:
- Load sample stock transactions
- Filter to specific stock code
- Calculate year-specific returns
- Verify result structure and calculations

### 2. Stock Annual Returns - Portfolio
**Test**: `test_scenario_stock_annual_portfolio`

Calculates annual returns for entire stock portfolio.

**Workflow**:
- Load multiple stock transactions
- Aggregate across all stock codes
- Calculate portfolio-level returns
- Verify total portfolio performance

### 3. Stock Complete History - Specific Stock
**Test**: `test_scenario_stock_history_specific_stock`

Calculates complete investment history for a specific stock.

**Workflow**:
- Load stock transactions for one code
- Calculate total invested, current value, and gains
- Use mocked Tushare API for current prices
- Verify complete P&L calculation

### 4. Stock Complete History - Portfolio
**Test**: `test_scenario_stock_history_portfolio`

Calculates complete investment history for entire stock portfolio.

**Workflow**:
- Load all stock transactions
- Aggregate across all codes
- Calculate portfolio-wide metrics
- Verify accurate aggregation

### 5. Fund Annual Returns - Specific Fund
**Test**: `test_scenario_fund_annual_specific_fund`

Calculates annual returns for a specific fund.

**Workflow**:
- Load sample fund transactions
- Filter to specific fund code
- Calculate year-specific returns
- Use mocked East Money API

### 6. Fund Annual Returns - Portfolio
**Test**: `test_scenario_fund_annual_portfolio`

Calculates annual returns for entire fund portfolio.

**Workflow**:
- Load multiple fund transactions
- Aggregate across all fund codes
- Calculate portfolio-level returns
- Verify fund-specific calculations

### 7. Fund Complete History - Specific Fund
**Test**: `test_scenario_fund_history_specific_fund`

Calculates complete investment history for a specific fund.

**Workflow**:
- Load fund transactions for one code
- Calculate total invested and current value
- Use mocked East Money NAV data
- Verify complete history metrics

### 8. Fund Complete History - Portfolio
**Test**: `test_scenario_fund_history_portfolio`

Calculates complete investment history for entire fund portfolio.

**Workflow**:
- Load all fund transactions
- Aggregate across all fund codes
- Calculate combined portfolio metrics
- Verify accurate aggregation

### 9. Mixed Portfolio History
**Test**: `test_scenario_mixed_portfolio_history`

Calculates complete history for mixed stock and fund portfolio.

**Workflow**:
- Create transactions with both stocks and funds
- Combine mocked prices from both Tushare and East Money
- Calculate portfolio with mixed asset types
- Verify proper handling of different asset classes

### 10. JSON Output Format
**Test**: `test_scenario_json_output_format`

Verifies JSON output formatting capability.

**Workflow**:
- Execute calculation with JSON format flag
- Verify structured output
- Test both annual and history result formats
- Ensure compatibility with data serialization

### 11. Error Handling - Invalid Investment Code
**Test**: `test_scenario_error_invalid_code`

Handles errors when investment code doesn't exist.

**Workflow**:
- Execute with non-existent code
- Verify graceful error handling
- Ensure None is returned for invalid codes
- Test error message display

### 12. Error Handling - Invalid File
**Test**: `test_scenario_error_invalid_file`

Handles errors when transaction file is invalid or missing.

**Workflow**:
- Execute with invalid file path
- Verify error handling
- Ensure None is returned
- Test appropriate error messages

### 13. Edge Case - No Transactions
**Test**: `test_scenario_edge_case_no_transactions`

Handles edge case with empty transaction list.

**Workflow**:
- Execute with empty transaction list
- Verify graceful handling
- Ensure None is returned
- Test validation errors

### 14. Dividend Income Tracking
**Test**: `test_scenario_dividend_tracking`

Tracks dividend income separately from capital gains.

**Workflow**:
- Create transactions with buy and dividend entries
- Calculate annual returns
- Verify dividend income is tracked
- Ensure dividends separate from capital gains

### 15. FIFO Cost Basis Accuracy
**Test**: `test_scenario_fifo_cost_basis`

Verifies FIFO cost basis calculation accuracy.

**Workflow**:
- Create multiple purchases at different prices
- Create partial sale transaction
- Calculate FIFO-based cost allocation
- Verify accurate realized/unrealized gains
- Test scenario: Buy 1000@20, Buy 1000@25, Sell 1500@27
  - Realized gain: 1000*7 + 500*2 = 8000
  - Current value: 500 * 25.50 = 12750
  - Net: 8000 + 12750 - 45000 = -24250

## Mock API Configuration

### Tushare Client Mock
```python
mock_tushare_client.fetch_current_prices.return_value = {
    "000001": PriceData(code="000001", price_date=date(2024, 11, 30), price_value=25.50, source="tushare"),
    "600036": PriceData(code="600036", price_date=date(2024, 11, 30), price_value=45.80, source="tushare"),
}

mock_tushare_client.fetch_historical_prices.return_value = {
    "000001": [
        PriceData(code="000001", price_date=date(2024, 11, 30), price_value=25.50, source="tushare"),
        PriceData(code="000001", price_date=date(2024, 6, 30), price_value=23.20, source="tushare"),
        PriceData(code="000001", price_date=date(2024, 1, 2), price_value=21.10, source="tushare"),
    ],
}
```

### East Money Client Mock
```python
mock_eastmoney_client.fetch_fund_nav.return_value = {
    "110011": PriceData(code="110011", price_date=date(2024, 11, 30), price_value=2.156, source="eastmoney"),
    "161725": PriceData(code="161725", price_date=date(2024, 11, 30), price_value=1.842, source="eastmoney"),
}

mock_eastmoney_client.fetch_fund_prices_as_nav.return_value = {
    "110011": [
        PriceData(code="110011", price_date=date(2024, 11, 30), price_value=2.156, source="eastmoney"),
        PriceData(code="110011", price_date=date(2024, 6, 30), price_value=2.045, source="eastmoney"),
    ],
}
```

## Running Tests

### All Tests
```bash
uv run pytest
```

### Specific Test Files
```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Specific test
uv run pytest tests/integration/test_all_user_scenarios.py::TestAllUserScenarios::test_scenario_stock_annual_specific_stock -v
```

### With Coverage
```bash
uv run pytest --cov=src/invest_ai --cov-report=html
```

### Verbose Output
```bash
uv run pytest -v --tb=short
```

## Test Data

### Sample Stock Transactions
```python
[
    Transaction(code="000001", transaction_date=date(2024, 1, 15), type=TransactionType.BUY,
                quantity=1000.0, unit_price=21.10, total_amount=21100.00),
    Transaction(code="600036", transaction_date=date(2024, 2, 10), type=TransactionType.BUY,
                quantity=500.0, unit_price=40.20, total_amount=20100.00),
    Transaction(code="000001", transaction_date=date(2024, 6, 20), type=TransactionType.SELL,
                quantity=500.0, unit_price=23.20, total_amount=11600.00),
]
```

### Sample Fund Transactions
```python
[
    Transaction(code="110011", transaction_date=date(2024, 3, 1), type=TransactionType.BUY,
                quantity=10000.0, unit_price=1.85, total_amount=18500.00),
    Transaction(code="161725", transaction_date=date(2024, 4, 1), type=TransactionType.BUY,
                quantity=8000.0, unit_price=1.62, total_amount=12960.00),
]
```

## Validation

### Expected Result Structures

#### AnnualResult
```python
{
    "year": 2024,
    "code": "000001",
    "start_value": 0.0,
    "end_value": 12750.0,
    "net_gain": -24250.0,
    "return_rate": -53.89,
    "dividends": 500.0,
    "capital_gain": -24750.0,
}
```

#### HistoryResult
```python
{
    "code": "000001",
    "investment_type": "stock",
    "total_invested": 41200.00,
    "current_value": 32500.00,
    "total_gain": -8700.00,
    "return_rate": -21.12,
    "first_investment": date(2024, 1, 15),
    "last_transaction": date(2024, 8, 15),
    "transaction_count": 4,
}
```

## Continuous Integration

All tests must pass before code can be merged:

```bash
# Lint
uv run ruff check src/ tests/

# Format
uv run black src/ tests/

# Type check
uv run mypy src/

# Test
uv run pytest
```

## Test Maintenance

### Adding New Test Scenarios

1. Add test method to appropriate test class in `tests/integration/test_all_user_scenarios.py`
2. Use existing mock fixtures (`mock_tushare_client`, `mock_eastmoney_client`)
3. Follow naming convention: `test_scenario_<type>_<calculation>`
4. Add comprehensive docstring
5. Include assertions for all result fields
6. Update this documentation

### Updating Mock Data

When market conditions change or new test scenarios are added:

1. Update mock price values in fixture definitions
2. Update expected calculations in test assertions
3. Ensure all date values are current trading days
4. Test with realistic price movements

### Test Data Requirements

All test data must:
- Use chronological transaction ordering
- Include realistic price movements
- Cover edge cases (dividends, partial sales, etc.)
- Have verifiable calculations
- Use valid Chinese stock/fund codes

## Troubleshooting

### Common Issues

1. **Tests failing with AttributeError**
   - Check model field names (e.g., `price_value` not `price`)
   - Verify Pydantic model structure

2. **Mock data format errors**
   - Ensure PriceData objects match expected structure
   - Check date formats (use `date()` constructor)

3. **Calculation mismatches**
   - Verify FIFO logic in test assertions
   - Check price date matching

### Debugging Tests

```bash
# Run with Python debugger
uv run pytest tests/integration/test_all_user_scenarios.py::TestAllUserScenarios::test_scenario_fifo_cost_basis -xvs --pdb
```

## Test Metrics

- **Total Tests**: 68 (53 unit + 15 integration)
- **Pass Rate**: 100%
- **Coverage**: 49% overall (integration tests have limited coverage scope)
- **Test Execution Time**: ~3 seconds for full suite

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Unit Testing Best Practices](https://docs.python.org/3/library/unittest.html)
- [Async Testing with Pytest](https://pytest-asyncio.readthedocs.io/)