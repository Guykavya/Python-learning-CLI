import sqlite3
from datetime import date, timedelta

import httpx

CREATE = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, order_date TEXT NOT NULL, status TEXT NOT NULL, amount TEXT NOT NULL
)
"""


def backfill(client: httpx.Client, conn: sqlite3.Connection, start: date, end: date) -> dict[str, int]:
    """Reload each day in [start, end]: fetch it fully, then delete + insert it in one transaction."""
    # for each day: fetch every page (store each id once) -> with conn: DELETE the day, insert the orders
    raise NotImplementedError("walk the days; fetch a whole day; then replace it in one transaction")
