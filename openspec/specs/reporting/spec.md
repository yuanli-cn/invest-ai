# Reporting

## Purpose
Output formatting and display of investment calculation results.

## Requirements

### Requirement: Annual Report Format
The system SHALL display annual returns in a formatted table showing key metrics.

#### Scenario: Display annual report
- **WHEN** annual calculation is complete
- **THEN** the report shows year, start value, end value, net gain/loss, return rate, and dividends

#### Scenario: Single investment annual report
- **WHEN** user specifies a specific investment code
- **THEN** the report header includes the investment type and code

#### Scenario: Portfolio annual report
- **WHEN** user does not specify a code
- **THEN** the report header shows "PORTFOLIO" with aggregated metrics

### Requirement: History Report Format
The system SHALL display complete history in a formatted table showing total metrics.

#### Scenario: Display history report
- **WHEN** history calculation is complete
- **THEN** the report shows total invested, current value, total P&L, and return rate

#### Scenario: Single investment history report
- **WHEN** user specifies a specific investment code
- **THEN** the report header includes "History" with the investment type and code

#### Scenario: Portfolio history report
- **WHEN** user does not specify a code
- **THEN** the report header shows "PORTFOLIO HISTORY"

### Requirement: Currency Formatting
The system SHALL format monetary values with currency symbol and thousands separators.

#### Scenario: Format positive amount
- **WHEN** displaying ¥10000.50
- **THEN** output is "¥10,000.50"

#### Scenario: Format negative amount
- **WHEN** displaying -¥500.00
- **THEN** output is "-¥500.00" or "¥-500.00"

### Requirement: Percentage Formatting
The system SHALL format percentages with two decimal places.

#### Scenario: Format positive percentage
- **WHEN** displaying 15.342% return rate
- **THEN** output is "15.34%"

#### Scenario: Format negative percentage
- **WHEN** displaying -2.5% return rate
- **THEN** output is "-2.50%"

### Requirement: JSON Output Format
The system SHALL output results in JSON format when requested.

#### Scenario: JSON annual result
- **WHEN** user specifies `--format json` for annual calculation
- **THEN** output is valid JSON with year, start_value, end_value, net_gain, return_rate fields

#### Scenario: JSON history result
- **WHEN** user specifies `--format json` for history calculation
- **THEN** output is valid JSON with total_invested, current_value, total_gain, return_rate fields

### Requirement: Box Drawing Display
The system SHALL use box drawing characters for visual report formatting.

#### Scenario: Report with borders
- **WHEN** displaying text format report
- **THEN** report uses Unicode box drawing characters (┌, ─, ┐, │, └, ┘)
