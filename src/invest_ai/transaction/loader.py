"""Transaction data loader for YAML files."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from invest_ai.models import Transaction, TransactionList, ValidationResult


class TransactionLoader:
    """Handles loading transactions from YAML files."""

    def __init__(self) -> None:
        """Initialize the transaction loader."""
        pass

    async def load_transactions(self, file_path: str) -> TransactionList:
        """Load transactions from a YAML file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Transaction file not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            # Read YAML file
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Handle both single transaction and list formats
            if data is None:
                return TransactionList(transactions=[])

            if isinstance(data, dict):
                # Handle directory format with different sections
                transactions = []

                # Handle investments section
                if "investments" in data:
                    investments = data["investments"]

                    # Process stocks
                    if "stocks" in investments:
                        for item in investments["stocks"]:
                            transaction = self._parse_transaction_dict(item)
                            if transaction:
                                transactions.append(transaction)

                    # Process funds
                    if "funds" in investments:
                        for item in investments["funds"]:
                            transaction = self._parse_transaction_dict(item)
                            if transaction:
                                transactions.append(transaction)

                # Handle dividends section
                if "dividends" in data:
                    for item in data["dividends"]:
                        transaction = self._parse_dividend_dict(item)
                        if transaction:
                            transactions.append(transaction)

                # Handle flat list format
                elif "transactions" in data:
                    for item in data["transactions"]:
                        transaction = self._parse_transaction_dict(item)
                        if transaction:
                            transactions.append(transaction)

                # Handle format where root is a transaction list
                else:
                    transaction = self._parse_transaction_dict(data)
                    if transaction:
                        transactions.append(transaction)

            elif isinstance(data, list):
                # Handle list of transactions
                transactions = []
                for item in data:
                    transaction = self._parse_transaction_dict(item)
                    if transaction:
                        transactions.append(transaction)
            else:
                raise ValueError("Invalid YAML format: expected list or dict")

            # Sort by date
            transactions.sort(key=lambda x: x.date)

            return TransactionList(transactions=transactions)

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}") from e
        except ValidationError as e:
            raise ValueError(f"Transaction validation failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading transactions: {e}") from e

    def _parse_transaction_dict(self, data: dict) -> Transaction | None:
        """Parse a transaction dictionary into a Transaction object."""
        if not data:
            return None

        try:
            # Ensure required fields are present
            required_fields = [
                "code",
                "date",
                "type",
                "quantity",
                "unit_price",
                "total_amount",
            ]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Parse date
            if isinstance(data["date"], str):
                from datetime import datetime

                try:
                    date_obj = datetime.strptime(data["date"], "%Y-%m-%d").date()
                except ValueError:
                    # Try other date formats
                    try:
                        date_obj = datetime.strptime(data["date"], "%Y-%m-%d").date()
                    except ValueError:
                        raise ValueError(
                            f"Invalid date format: {data['date']}"
                        ) from None
            else:
                date_obj = data["date"]

            # Create transaction
            transaction_data = {
                "code": str(data["code"]).zfill(6),  # Ensure 6-digit format
                "date": date_obj,
                "type": data["type"],
                "quantity": float(data["quantity"]),
                "unit_price": float(data["unit_price"]),
                "total_amount": float(data["total_amount"]),
            }

            # Add optional dividend fields
            if "amount_per_share" in data:
                transaction_data["amount_per_share"] = float(data["amount_per_share"])

            return Transaction(**transaction_data)

        except Exception as e:
            raise ValueError(f"Error parsing transaction {data}: {e}") from e

    def _parse_dividend_dict(self, data: dict) -> Transaction | None:
        """Parse a dividend dictionary into a Transaction object."""
        if not data:
            return None

        try:
            # Determine dividend type based on data content and create appropriate transaction
            if data.get("amount", data.get("total_amount", 0)) > 0:
                # Cash dividend: quantity and unit_price are 0, total_amount is the cash received
                transaction_data = {
                    "code": str(data["code"]).zfill(6),
                    "date": data["date"],
                    "type": "dividend",
                    "quantity": 0.0,
                    "unit_price": 0.0,
                    "total_amount": float(
                        data.get("amount", data.get("total_amount", 0))
                    ),
                }
            elif data.get("quantity", data.get("share_amount", 0)) > 0:
                # Stock dividend/reinvestment: unit_price is 0, quantity is shares received
                transaction_data = {
                    "code": str(data["code"]).zfill(6),
                    "date": data["date"],
                    "type": "dividend",
                    "quantity": float(
                        data.get("quantity", data.get("share_amount", 0))
                    ),
                    "unit_price": 0.0,
                    "total_amount": 0.0,
                }
            else:
                raise ValueError(
                    "Dividend must have either positive amount (cash) or positive quantity (stock)"
                )

            return Transaction(**transaction_data)

        except Exception as e:
            raise ValueError(f"Error parsing dividend {data}: {e}") from e

    async def validate_file_format(self, file_path: str) -> ValidationResult:
        """Validate that the file format is correct without processing all transactions."""
        try:
            path = Path(file_path)

            if not path.exists():
                return ValidationResult(
                    is_valid=False, errors=[f"File not found: {file_path}"]
                )

            # Try to load and parse the file
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                return ValidationResult(is_valid=False, errors=["YAML file is empty"])

            return ValidationResult(is_valid=True)

        except yaml.YAMLError as e:
            return ValidationResult(is_valid=False, errors=[f"YAML format error: {e}"])
        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[f"File validation error: {e}"]
            )
