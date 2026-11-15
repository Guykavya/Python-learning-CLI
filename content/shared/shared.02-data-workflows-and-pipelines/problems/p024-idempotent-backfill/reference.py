import sqlite3
from datetime import date, timedelta

import httpx

CREATE = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, order_date TEXT NOT NULL, status TEXT NOT NULL, amount TEXT NOT NULL
)
"""

UPSERT = """
INSERT INTO orders (id, order_date, status, amount) VALUES (:id, :order_date, :status, :amount)
ON CONFLICT (id) DO UPDATE SET
    order_date = excluded.order_date, status = excluded.status, amount = excluded.amount
"""


def fetch_day(client: httpx.Client, day: str) -> list[dict]:
    """All orders of one day, one entry per id (pages may repeat an order)."""
    by_id: dict[int, dict] = {}
    page = 1
    while page is not None:
        response = client.get("/v1/orders", params={"created_on": day, "page": page})
        response.raise_for_status()
        body = response.json()
        for order in body["data"]:
            by_id[order["id"]] = order
        page = body["next_page"]
    return list(by_id.values())


def days_between(start: date, end: date):
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def backfill(client: httpx.Client, conn: sqlite3.Connection, start: date, end: date) -> dict[str, int]:
    """Reload each day in [start, end]: fetch it fully, then delete + insert it in one transaction."""
    if start > end:
        raise ValueError(f"start {start} is after end {end}")
    conn.execute(CREATE)
    counts = {}
    for day in days_between(start, end):
        key = day.isoformat()
        orders = fetch_day(client, key)                  # 1. extract the whole partition first
        rows = [{"id": o["id"], "order_date": key, "status": o["status"], "amount": o["amount"]}
                for o in orders]
        with conn:                                       # 2. replace it atomically
            conn.execute("DELETE FROM orders WHERE order_date = ?", (key,))
            conn.executemany(UPSERT, rows)               # 3. upsert: an order moved from another day
        counts[key] = len(rows)
    return counts
