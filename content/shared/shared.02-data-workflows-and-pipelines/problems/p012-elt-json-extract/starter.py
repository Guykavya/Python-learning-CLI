import sqlite3


def load_raw(conn, payloads, loaded_at):
    """Store each JSON text as-is in raw_orders; return the number of rows inserted."""
    return 0


def build_clean(conn):
    """Rebuild clean_orders from raw_orders with one CREATE TABLE ... AS SELECT; return its row count."""
    return 0
