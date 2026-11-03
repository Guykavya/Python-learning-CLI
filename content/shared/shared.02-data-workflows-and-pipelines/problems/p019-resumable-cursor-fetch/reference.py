import json
import os
import sqlite3
from pathlib import Path

import httpx

CREATE = "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL, updated_at TEXT NOT NULL)"

UPSERT = """
INSERT INTO orders (id, status, updated_at) VALUES (:id, :status, :updated_at)
ON CONFLICT (id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at
"""


def save_checkpoint(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state), encoding="utf-8")
    os.replace(tmp, path)


def fetch_resumable(client: httpx.Client, conn: sqlite3.Connection, checkpoint_path, limit: int = 3) -> int:
    """Cursor-paginate into SQLite; checkpoint after each committed page; resume if a checkpoint exists."""
    checkpoint_path = Path(checkpoint_path)
    conn.execute(CREATE)
    cursor = None
    if checkpoint_path.exists():
        cursor = json.loads(checkpoint_path.read_text(encoding="utf-8"))["cursor"]

    written = 0
    while True:
        params = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        response = client.get("/v1/orders", params=params)
        response.raise_for_status()
        body = response.json()
        rows = [{"id": o["id"], "status": o["status"], "updated_at": o["updated_at"]} for o in body["items"]]
        with conn:                                      # 1. the data is durable ...
            conn.executemany(UPSERT, rows)
        written += len(rows)
        cursor = body["next_cursor"]
        if cursor is None:
            break
        save_checkpoint(checkpoint_path, {"cursor": cursor})   # 2. ... before we claim it is

    checkpoint_path.unlink(missing_ok=True)             # finished: next run starts fresh
    return written
