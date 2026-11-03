## Approach

A watermark is a promise: "everything up to this point is safely in the table". Two rules keep
that promise true.

1. **The watermark is the maximum, not the last.** The API sorts by id, so the last record of
   the last page can be older than records before it. Using it as the watermark would make the
   next run fetch the newer ones again (harmless here because of the upsert, but wasteful) or,
   with a different sort order, could move the watermark *backwards*.
2. **Data and watermark change together.** If the watermark were stored before the data, or
   committed page by page while the data was not, a crash could leave a watermark that claims
   orders are loaded when they are not. Those orders would be skipped forever, because the API
   only returns `updated_at > watermark`. With both writes in one transaction, a failed run
   changes nothing and the next run simply repeats it.

The reference fetches all pages into a list first, then writes inside `with conn:`. A network
error therefore happens before any write, and an SQL error rolls back.

## Code

```python
import sqlite3
import httpx

WATERMARK = "orders.updated_at"


def read_watermark(conn):
    row = conn.execute("SELECT value FROM pipeline_state WHERE name = ?", (WATERMARK,)).fetchone()
    return row[0] if row else None


def fetch_changed(client, since, per_page):
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


def run_incremental(client, conn, per_page=3):
    conn.executescript(SCHEMA)                        # the two CREATE TABLE IF NOT EXISTS
    records = fetch_changed(client, read_watermark(conn), per_page)
    rows = [{k: r[k] for k in ("id", "status", "amount", "updated_at")} for r in records]
    with conn:
        conn.executemany(UPSERT_ORDER, rows)          # INSERT ... ON CONFLICT (id) DO UPDATE ...
        if rows:
            conn.execute(SET_STATE, (WATERMARK, max(r["updated_at"] for r in rows)))
    return len(rows)
```

## Complexity

O(c) requests and row writes for c changed orders (plus one request when nothing changed),
instead of O(n) for all n orders on every run. Memory is O(c) because the changed records are
held until the commit.

## Another way

Write each page as it arrives, all inside one transaction, and `commit()` only after the last
page (with `rollback()` in an `except` that re-raises). This uses less memory for huge
extracts, at the cost of a long-open transaction.

This problem's API uses `>`. Records that share the watermark's exact timestamp but are
committed on the server *after* your run are then missed. p016 traces that case; the usual
cures are `>=` plus an idempotent upsert, or a small overlap window (`updated_since =
watermark - 5 minutes`), both of which re-fetch a few rows on purpose.
