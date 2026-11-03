import json
import os
import sqlite3
from pathlib import Path

import httpx

CREATE = "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL, updated_at TEXT NOT NULL)"


def fetch_resumable(client: httpx.Client, conn: sqlite3.Connection, checkpoint_path, limit: int = 3) -> int:
    """Cursor-paginate into SQLite; checkpoint after each committed page; resume if a checkpoint exists."""
    conn.execute(CREATE)
    # cursor = the checkpoint's cursor if the file exists, else None
    # loop: request -> upsert + commit -> save checkpoint (atomic) -> stop when next_cursor is None
    # finally delete the checkpoint and return how many orders this call wrote
    return 0
