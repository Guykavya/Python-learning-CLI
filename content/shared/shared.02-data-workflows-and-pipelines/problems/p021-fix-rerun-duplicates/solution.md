## Approach

**Bug 1: the write is not idempotent.** The table has no key and the code appends with a plain
`INSERT`. Every run (the scheduler's, the engineer's, a resume that repeats a page) adds another
copy. The fix is to say what makes an order unique (`id INTEGER PRIMARY KEY`) and write with an
UPSERT, so writing the same order again *replaces* it with the newest values instead of adding
a copy. `INSERT OR IGNORE` is not enough: it would keep yesterday's values for an order that
changed.

**Bug 2: the checkpoint is saved before the work it describes.** The buggy loop does

```
request page 2 -> save checkpoint "next_page": 3 -> transform (crash!) -> write
```

so when `transform` crashed on order 105, the checkpoint already said "page 2 is done". The
resume trusted it and started at page 3: orders 104-106 were never written and nobody got an
error. Moving the save just below `transform` is not enough, because the database write can fail
too (a value SQLite cannot store, a full disk, a locked file). The checkpoint may only move
**after the commit**:

```
request page 2 -> transform -> write + commit -> save checkpoint "next_page": 3
```

Now every crash leaves the checkpoint at the page that was not finished. The worst case is a
crash *between* the commit and the save; then the resume writes page `k` again, which bug 1's
fix (the upsert) makes harmless. The two fixes need each other: at-least-once processing plus
an idempotent write.

## Code

```python
UPSERT = """
INSERT INTO orders (id, status, amount, qty, updated_at)
VALUES (:id, :status, :amount, :qty, :updated_at)
ON CONFLICT (id) DO UPDATE SET
    status = excluded.status, amount = excluded.amount,
    qty = excluded.qty, updated_at = excluded.updated_at
"""


def run(client, db_path, checkpoint_path, per_page=3):
    checkpoint_path = Path(checkpoint_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS orders "
            "(id INTEGER PRIMARY KEY, status TEXT, amount TEXT, qty INTEGER, updated_at TEXT)"
        )
        page = load_checkpoint(checkpoint_path)["next_page"]
        loaded = 0
        while page is not None:
            response = client.get("/v1/orders", params={"page": page, "per_page": per_page})
            response.raise_for_status()
            body = response.json()
            rows = [transform(order) for order in body["data"]]
            with conn:
                conn.executemany(UPSERT, rows)
            loaded += len(rows)
            page = body["next_page"]
            save_checkpoint(checkpoint_path, {"next_page": page})
        checkpoint_path.unlink(missing_ok=True)
        return loaded
    finally:
        conn.close()
```

(`load_checkpoint`, `save_checkpoint` and `transform` are unchanged.)

## Complexity

Unchanged: one request and one transaction per page. A resume repeats at most one page.

## Another way

`INSERT OR REPLACE` with the primary key also fixes bug 1 here, because every column is
rewritten. It deletes and re-inserts the row, though, which fires delete triggers and breaks
foreign keys that point at the order; `ON CONFLICT DO UPDATE` changes the row in place.

To remove bug 2's whole class of problems, keep the checkpoint **in the same database** as a row
in a state table and update it inside the same `with conn:` block as the page. Then data and
checkpoint can never disagree.

To clean up a table that incident 1 already doubled, deduplicate before adding the key, for
example `DELETE FROM orders WHERE rowid NOT IN (SELECT MAX(rowid) FROM orders GROUP BY id)`.
