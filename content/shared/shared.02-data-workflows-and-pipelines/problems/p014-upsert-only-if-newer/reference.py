import sqlite3

CREATE = """
CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY,
    status     TEXT NOT NULL,
    amount     TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""

UPSERT = """
INSERT INTO orders (id, status, amount, updated_at)
VALUES (:id, :status, :amount, :updated_at)
ON CONFLICT (id) DO UPDATE SET
    status     = excluded.status,
    amount     = excluded.amount,
    updated_at = excluded.updated_at
WHERE excluded.updated_at > orders.updated_at
"""


def upsert_if_newer(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """Insert new ids; update an existing id only when the incoming updated_at is later."""
    conn.execute(CREATE)
    with conn:                                   # commit on success, roll back on error
        cursor = conn.executemany(UPSERT, rows)
    return cursor.rowcount                       # rows inserted + rows really updated
