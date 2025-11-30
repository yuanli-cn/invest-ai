# CLI Interface

## Purpose
Command-line interface for investment profit and loss calculation.

## Requirements

### Requirement: Investment Type Selection
The CLI SHALL require an investment type parameter (`--type`) with valid values `stock` or `fund`.

#### Scenario: Stock type specified
- **WHEN** user runs `invest-ai --type stock --data transactions.yaml`
- **THEN** the system processes stock transactions

#### Scenario: Fund type specified
- **WHEN** user runs `invest-ai --type fund --data transactions.yaml`
- **THEN** the system processes fund transactions

#### Scenario: Invalid type specified
- **WHEN** user runs `invest-ai --type invalid --data transactions.yaml`
- **THEN** the system displays an error message and exits with code 1

### Requirement: Transaction Data File
The CLI SHALL require a transaction data file parameter (`--data`) pointing to a valid YAML file.

#### Scenario: Valid data file
- **WHEN** user provides `--data transactions.yaml` with a valid YAML file
- **THEN** the system loads and processes transactions

#### Scenario: Missing data file
- **WHEN** user provides `--data nonexistent.yaml` with a non-existent file
- **THEN** the system displays "File not found" error and exits with code 1

#### Scenario: Default data file by type
- **WHEN** user omits `--data` with `--type stock`
- **THEN** the system uses `data/stock.yaml` as default

### Requirement: Optional Year Filter
The CLI SHALL accept an optional year parameter (`--year`) for annual return calculations.

#### Scenario: Year specified
- **WHEN** user runs `invest-ai --type stock --year 2023 --data tx.yaml`
- **THEN** the system calculates returns for year 2023 only

#### Scenario: No year specified
- **WHEN** user runs `invest-ai --type stock --data tx.yaml` without `--year`
- **THEN** the system calculates complete history from first transaction to current date

### Requirement: Optional Investment Code Filter
The CLI SHALL accept an optional investment code parameter (`--code`) to filter by specific investment.

#### Scenario: Code specified
- **WHEN** user runs `invest-ai --type stock --code 000001 --data tx.yaml`
- **THEN** the system calculates returns for stock 000001 only

#### Scenario: No code specified
- **WHEN** user runs `invest-ai --type stock --data tx.yaml` without `--code`
- **THEN** the system calculates returns for all investments of the specified type

### Requirement: Output Format Selection
The CLI SHALL accept an optional format parameter (`--format`) with values `text` (default) or `json`.

#### Scenario: Default text format
- **WHEN** user runs without `--format` parameter
- **THEN** the system outputs human-readable formatted text

#### Scenario: JSON format
- **WHEN** user runs with `--format json`
- **THEN** the system outputs JSON-formatted results

### Requirement: Help Display
The CLI SHALL display help information when invoked with `--help` or without arguments.

#### Scenario: Help flag
- **WHEN** user runs `invest-ai --help`
- **THEN** the system displays usage information and available options

#### Scenario: No arguments
- **WHEN** user runs `invest-ai` without any arguments
- **THEN** the system displays a help summary
