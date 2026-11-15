import sqlite3

import httpx

WATERMARK = "orders.updated_at"

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pipeline_state (name TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def run_incremental(client: httpx.Client, conn: sqlite3.Connection, per_page: int = 3) -> int:
    """Load orders changed since the stored watermark; store data and watermark together."""
    conn.executescript(SCHEMA)
    # 1. read the watermark (None on the first run)
    # 2. fetch all pages; send updated_since only when there is a watermark
    # 3. + 4. in ONE transaction: upsert the orders, store max(updated_at) as the new watermark
    raise NotImplementedError("read watermark -> fetch pages -> upsert + new watermark in one transaction")
