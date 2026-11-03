import sqlite3

CREATE_RAW = """
CREATE TABLE IF NOT EXISTS raw_orders (
    raw_id    INTEGER PRIMARY KEY,
    loaded_at TEXT NOT NULL,
    payload   TEXT NOT NULL
)
"""

BUILD_CLEAN = """
CREATE TABLE clean_orders AS
SELECT
    CAST(json_extract(payload, '$.id') AS INTEGER)                          AS id,
    lower(trim(json_extract(payload, '$.customer.email')))                  AS email,
    NULLIF(trim(json_extract(payload, '$.customer.city')), '')              AS city,
    lower(trim(json_extract(payload, '$.status')))                          AS status,
    CAST(ROUND(CAST(json_extract(payload, '$.amount') AS REAL) * 100) AS INTEGER) AS amount_cents,
    upper(json_extract(payload, '$.currency'))                              AS currency,
    json_extract(payload, '$.created_at')                                   AS created_at,
    json_array_length(payload, '$.items')                                   AS item_count
FROM raw_orders
WHERE json_valid(payload)
"""


def load_raw(conn, payloads, loaded_at):
    """Store each JSON text as-is in raw_orders; return the number of rows inserted."""
    conn.execute(CREATE_RAW)
    rows = [(loaded_at, text) for text in payloads]
    conn.executemany("INSERT INTO raw_orders (loaded_at, payload) VALUES (?, ?)", rows)
    conn.commit()
    return len(rows)


def build_clean(conn):
    """Rebuild clean_orders from raw_orders with one CREATE TABLE ... AS SELECT; return its row count."""
    conn.execute("DROP TABLE IF EXISTS clean_orders")
    conn.execute(BUILD_CLEAN)
    conn.commit()
    return conn.execute("SELECT COUNT(*) FROM clean_orders").fetchone()[0]
