## Approach

The checkpoint is a claim: "everything before this cursor is safely stored". The code must make
that claim true at every instant, including the instant the process dies.

| Crash point | Committed | Checkpoint says | Resume does | Result |
|---|---|---|---|---|
| request of page k fails | pages 1..k-1 | page k | fetches page k | nothing lost, nothing repeated |
| after commit of page k, before its checkpoint | pages 1..k | page k (one behind) | fetches page k **again** | the upsert rewrites the same rows: no duplicates |
| during the atomic save | pages 1..k | page k (old file intact) | fetches page k again | same as above |
| after the last page, before the delete | all | the last page | fetches the last page again | harmless |

Now flip the order (checkpoint first, then commit): a crash between them leaves a checkpoint that
points **past** page k while page k was never committed. The resume skips it, and those orders
are lost without any error. That is why it is always **data first, checkpoint second**, and why
the write must be idempotent: the price of the safe order is that one page may be loaded twice.

This gives **at-least-once** processing (every page is written one or more times) plus an
**idempotent sink** (writing it again changes nothing), which together behave like exactly-once.

## Code

```python
import json
import os
from pathlib import Path

UPSERT = """
INSERT INTO orders (id, status, updated_at) VALUES (:id, :status, :updated_at)
ON CONFLICT (id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at
"""


def save_checkpoint(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state), encoding="utf-8")
    os.replace(tmp, path)


def fetch_resumable(client, conn, checkpoint_path, limit=3):
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
        with conn:
            conn.executemany(UPSERT, rows)
        written += len(rows)
        cursor = body["next_cursor"]
        if cursor is None:
            break
        save_checkpoint(checkpoint_path, {"cursor": cursor})
    checkpoint_path.unlink(missing_ok=True)
    return written
```

## Complexity

One request and one transaction per page. A resume after a crash on page k of p pages makes
p - k + 1 requests instead of p; at most one page is fetched twice.

## Another way

Store the cursor in the **same SQLite database**, in a `pipeline_state` table, and update it in
the same transaction as the page's rows (as p015 does with its watermark). Then "data written but
checkpoint not" cannot happen at all, and no page is ever repeated. A file checkpoint is still
common when the sink is not a database (Parquet files, an object store) and cannot share a
transaction with the state.

Beware: some APIs' cursors expire (for example after 24 hours). A robust resume catches the
"unknown cursor" 400 response, logs it, and falls back to a full run, which the upsert makes safe.
