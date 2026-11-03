import json
import os
import sqlite3
from pathlib import Path

import httpx


def load_checkpoint(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"next_page": 1}


def save_checkpoint(path: Path, state: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state), encoding="utf-8")
    os.replace(tmp, path)


def transform(order: dict) -> dict:
    return {
        "id": order["id"],
        "status": order["status"],
        "amount": order["amount"],
        "qty": sum(item["qty"] for item in order["items"]),
        "updated_at": order["updated_at"],
    }


def run(client: httpx.Client, db_path, checkpoint_path, per_page: int = 3) -> int:
    """Load every order page by page into SQLite; resume from the checkpoint after a crash."""
    checkpoint_path = Path(checkpoint_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS orders "
            "(id INTEGER, status TEXT, amount TEXT, qty INTEGER, updated_at TEXT)"
        )
        page = load_checkpoint(checkpoint_path)["next_page"]
        loaded = 0
        while page is not None:
            response = client.get("/v1/orders", params={"page": page, "per_page": per_page})
            response.raise_for_status()
            body = response.json()
            save_checkpoint(checkpoint_path, {"next_page": body["next_page"]})
            rows = [transform(order) for order in body["data"]]
            with conn:
                conn.executemany(
                    "INSERT INTO orders VALUES (:id, :status, :amount, :qty, :updated_at)", rows
                )
            loaded += len(rows)
            page = body["next_page"]
        checkpoint_path.unlink(missing_ok=True)
        return loaded
    finally:
        conn.close()
