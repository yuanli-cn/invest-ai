# Investment Calculation

## Purpose
Core calculation logic for investment profit and loss using FIFO cost allocation.

## Requirements

### Requirement: FIFO Cost Basis Allocation
The system SHALL allocate cost basis using First-In-First-Out method when selling investments.

#### Scenario: Simple FIFO allocation
- **WHEN** user bought 100 shares at ¥10, then 100 shares at ¥12, then sells 150 shares
- **THEN** cost basis is 100×¥10 + 50×¥12 = ¥1,600

#### Scenario: Complete lot exhaustion
- **WHEN** user bought 100 shares at ¥10, then sells exactly 100 shares
- **THEN** cost basis is 100×¥10 = ¥1,000 and the lot is fully consumed

#### Scenario: Insufficient inventory
- **WHEN** user attempts to sell more shares than currently held
- **THEN** the system raises an "Insufficient inventory" error

### Requirement: Realized Gain Calculation
The system SHALL calculate realized gains when shares are sold.

#### Scenario: Profitable sale
- **WHEN** cost basis is ¥1,000 and sale proceeds are ¥1,500
- **THEN** realized gain is ¥500

#### Scenario: Loss sale
- **WHEN** cost basis is ¥1,000 and sale proceeds are ¥800
- **THEN** realized loss is -¥200

### Requirement: Unrealized Gain Calculation
The system SHALL calculate unrealized gains for current holdings using market prices.

#### Scenario: Calculate unrealized gain
- **WHEN** user holds 100 shares with cost basis ¥1,000 and current price is ¥15
- **THEN** unrealized gain is 100×¥15 - ¥1,000 = ¥500

### Requirement: Annual Return Calculation
The system SHALL calculate returns for a specific calendar year.

#### Scenario: Full year with holdings
- **WHEN** calculating 2023 returns with start holdings of ¥10,000 and end holdings of ¥12,000
- **THEN** return rate is (¥12,000 - ¥10,000) / ¥10,000 = 20%

#### Scenario: Year with no starting position
- **WHEN** calculating 2023 returns with no holdings at start but ¥5,000 invested mid-year
- **THEN** the system calculates returns based on capital invested during the year

#### Scenario: Year with realized gains
- **WHEN** calculating 2023 returns including sales during the year
- **THEN** realized gains from 2023 sales are included in the return calculation

### Requirement: Complete History Calculation
The system SHALL calculate total returns from first investment to current date.

#### Scenario: Calculate complete history
- **WHEN** user requests complete history for an investment
- **THEN** the system returns total invested, current value, total P&L, and overall return rate

#### Scenario: History with no current holdings
- **WHEN** all shares have been sold
- **THEN** the system shows total realized gains and 0 current value

### Requirement: Portfolio Aggregation
The system SHALL aggregate calculations across multiple investments.

#### Scenario: Portfolio annual returns
- **WHEN** user requests annual returns for all stocks
- **THEN** the system aggregates start value, end value, and returns across all stock holdings

#### Scenario: Portfolio complete history
- **WHEN** user requests complete history for all investments
- **THEN** the system aggregates total invested, current value, and P&L across all holdings

### Requirement: Dividend Handling
The system SHALL track dividend income separately from capital gains.

#### Scenario: Cash dividend
- **WHEN** a cash dividend transaction is recorded
- **THEN** the dividend amount is added to total dividend income

#### Scenario: Stock dividend
- **WHEN** a stock dividend transaction is recorded
- **THEN** new shares are added with zero cost basis

### Requirement: Return Rate Calculation
The system SHALL calculate return rate as percentage gain over invested capital.

#### Scenario: Positive return rate
- **WHEN** total gain is ¥500 on ¥10,000 invested
- **THEN** return rate is 5.00%

#### Scenario: Negative return rate
- **WHEN** total loss is -¥200 on ¥10,000 invested
- **THEN** return rate is -2.00%

#### Scenario: Zero investment
- **WHEN** no capital has been invested
- **THEN** return rate is 0.00%
