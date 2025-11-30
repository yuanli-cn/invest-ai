# Market Data

## Purpose
Fetching market prices for stocks and NAV for mutual funds from external APIs.

## Requirements

### Requirement: Stock Price Fetching
The system SHALL fetch stock prices from Tushare Pro API using the configured token.

#### Scenario: Fetch current stock price
- **WHEN** a valid stock code and current date are provided
- **THEN** the system returns the closing price from Tushare

#### Scenario: Fetch historical stock price
- **WHEN** a valid stock code and historical date are provided
- **THEN** the system returns the closing price for that date

#### Scenario: Invalid stock code
- **WHEN** an invalid stock code is provided
- **THEN** the system raises a "Stock not found" error

#### Scenario: Missing Tushare token
- **WHEN** TUSHARE_TOKEN environment variable is not set
- **THEN** the system raises a configuration error

### Requirement: Fund NAV Fetching
The system SHALL fetch mutual fund NAV from East Money API.

#### Scenario: Fetch current fund NAV
- **WHEN** a valid fund code is provided
- **THEN** the system returns the latest NAV from East Money

#### Scenario: Fetch historical fund NAV
- **WHEN** a valid fund code and historical date are provided
- **THEN** the system returns the NAV for that date

#### Scenario: Invalid fund code
- **WHEN** an invalid fund code is provided
- **THEN** the system raises a "Fund not found" error

### Requirement: Trading Day Handling
The system SHALL handle non-trading days by finding the nearest trading day.

#### Scenario: Weekend date
- **WHEN** a price is requested for a Saturday or Sunday
- **THEN** the system returns the price from the previous Friday

#### Scenario: Holiday date
- **WHEN** a price is requested for a Chinese market holiday
- **THEN** the system returns the price from the nearest prior trading day

### Requirement: API Error Handling
The system SHALL gracefully handle API failures with retries and fallbacks.

#### Scenario: API timeout
- **WHEN** the API request times out
- **THEN** the system retries up to 3 times with exponential backoff

#### Scenario: API unavailable
- **WHEN** all API retries fail
- **THEN** the system reports a warning and continues with available data

### Requirement: Price Data Model
The system SHALL return price data with date, close price, and source information.

#### Scenario: Stock price data
- **WHEN** a stock price is fetched successfully
- **THEN** the returned PriceData contains date, close, and source="tushare"

#### Scenario: Fund NAV data
- **WHEN** a fund NAV is fetched successfully
- **THEN** the returned PriceData contains date, nav, and source="eastmoney"
