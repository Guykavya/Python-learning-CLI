import sqlite3
from collections import Counter
from decimal import Decimal, InvalidOperation

STATUSES = {"shipped", "pending", "cancelled"}

CREATE = "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL)"


class TooManyBadRecords(Exception):
    """Raised when the share of bad records is above the threshold. Has a .summary attribute."""

    def __init__(self, message: str, summary: dict):
        super().__init__(message)
        self.summary = summary


def load_with_threshold(conn: sqlite3.Connection, records: list, max_bad_ratio: float = 0.1) -> dict:
    """Skip bad records with reasons; abort (write nothing) if too many are bad."""
    # 1. check every record -> good rows, failures [(index, reason)]
    # 2. summary; if bad / total > max_bad_ratio: raise TooManyBadRecords(message, summary)
    # 3. otherwise upsert the good rows in one transaction and return the summary
    raise NotImplementedError("validate all first, then decide, then write")
