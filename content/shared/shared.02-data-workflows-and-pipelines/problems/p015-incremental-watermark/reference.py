import sqlite3

import httpx

WATERMARK = "orders.updated_at"

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pipeline_state (name TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

UPSERT_ORDER = """
INSERT INTO orders (id, status, amount, updated_at) VALUES (:id, :status, :amount, :updated_at)
ON CONFLICT (id) DO UPDATE SET
    status = excluded.status, amount = excluded.amount, updated_at = excluded.updated_at
"""

SET_STATE = """
INSERT INTO pipeline_state (name, value) VALUES (?, ?)
ON CONFLICT (name) DO UPDATE SET value = excluded.value
"""


def read_watermark(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT value FROM pipeline_state WHERE name = ?", (WATERMARK,)).fetchone()
    return row[0] if row else None


def fetch_changed(client: httpx.Client, since: str | None, per_page: int) -> list[dict]:
    params = {"page": 1, "per_page": per_page}
    if since is not None:
        params["updated_since"] = since
    records = []
    while True:
        response = client.get("/v1/orders", params=params)
        response.raise_for_status()
        body = response.json()
        records.extend(body["data"])
        if body["next_page"] is None:
            return records
        params["page"] = body["next_page"]


def run_incremental(client: httpx.Client, conn: sqlite3.Connection, per_page: int = 3) -> int:
    """Load orders changed since the stored watermark; store data and watermark together."""
    conn.executescript(SCHEMA)
    since = read_watermark(conn)
    records = fetch_changed(client, since, per_page)      # extract everything first
    rows = [{k: r[k] for k in ("id", "status", "amount", "updated_at")} for r in records]
    with conn:                                            # one transaction: data + watermark
        conn.executemany(UPSERT_ORDER, rows)
        if rows:
            conn.execute(SET_STATE, (WATERMARK, max(r["updated_at"] for r in rows)))
    return len(rows)
