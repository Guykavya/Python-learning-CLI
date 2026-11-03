import sqlite3

CREATE = """
CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY,
    status     TEXT NOT NULL,
    amount     TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def upsert_if_newer(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """Insert new ids; update an existing id only when the incoming updated_at is later."""
    conn.execute(CREATE)
    # TODO: INSERT ... ON CONFLICT (id) DO UPDATE SET ... WHERE <incoming is newer>
    # TODO: commit, and return how many rows were inserted or really updated
    return 0
