# Transaction Processing

## Purpose
Loading, validation, and filtering of investment transactions from YAML files.

## Requirements

### Requirement: YAML Transaction Loading
The system SHALL load transaction data from YAML files with support for buy, sell, and dividend transaction types.

#### Scenario: Load valid YAML file
- **WHEN** a valid YAML file with transaction records is provided
- **THEN** the system parses all transactions into Transaction objects

#### Scenario: Load empty YAML file
- **WHEN** an empty YAML file is provided
- **THEN** the system returns an empty transaction list without error

#### Scenario: Load malformed YAML file
- **WHEN** a YAML file with invalid syntax is provided
- **THEN** the system raises a validation error with line number

### Requirement: Transaction Field Validation
The system SHALL validate that each transaction contains required fields based on transaction type.

#### Scenario: Valid buy transaction
- **WHEN** a buy transaction has code, date, quantity, unit_price, and total_amount
- **THEN** the transaction passes validation

#### Scenario: Valid sell transaction
- **WHEN** a sell transaction has code, date, quantity, unit_price, and total_amount
- **THEN** the transaction passes validation

#### Scenario: Valid dividend transaction
- **WHEN** a dividend transaction has code, date, and total_amount
- **THEN** the transaction passes validation

#### Scenario: Missing required field
- **WHEN** a transaction is missing a required field
- **THEN** the system reports a validation error with field name

### Requirement: Investment Code Format Validation
The system SHALL validate that investment codes are 6-digit numeric strings.

#### Scenario: Valid stock code
- **WHEN** code is "000001" (6 digits)
- **THEN** the code passes validation

#### Scenario: Invalid code format
- **WHEN** code is "12345" (5 digits) or contains letters
- **THEN** the system reports an invalid code format error

### Requirement: Transaction Filtering by Type
The system SHALL filter transactions by investment type (stock or fund).

#### Scenario: Filter stock transactions
- **WHEN** filter criteria specifies investment_type="stock"
- **THEN** only transactions matching stock codes are returned

#### Scenario: Filter fund transactions
- **WHEN** filter criteria specifies investment_type="fund"
- **THEN** only transactions matching fund codes are returned

### Requirement: Transaction Filtering by Year
The system SHALL filter transactions by year for annual calculations.

#### Scenario: Filter by specific year
- **WHEN** filter criteria specifies year=2023
- **THEN** only transactions with dates in 2023 are returned

#### Scenario: Filter before year
- **WHEN** filter criteria specifies before_year=2023
- **THEN** only transactions with dates before 2023-01-01 are returned

### Requirement: Transaction Filtering by Code
The system SHALL filter transactions by specific investment code.

#### Scenario: Filter by code
- **WHEN** filter criteria specifies code="000001"
- **THEN** only transactions for code 000001 are returned

### Requirement: Transaction Chronological Sorting
The system SHALL sort transactions chronologically by date for processing.

#### Scenario: Sort transactions
- **WHEN** transactions are loaded from YAML
- **THEN** they are sorted by date in ascending order
