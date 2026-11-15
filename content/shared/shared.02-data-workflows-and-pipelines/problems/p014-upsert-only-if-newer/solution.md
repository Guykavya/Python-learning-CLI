## Approach

An **idempotent** write is one you can repeat without changing the result. A conditional UPSERT
is idempotent and also safe against stale data:

| incoming row | stored row | result |
|---|---|---|
| new id | none | insert |
| `updated_at` later | older | update all columns |
| `updated_at` equal | same version | keep (no change) |
| `updated_at` earlier | newer | keep (stale data ignored) |

SQLite does all four cases in one statement: the `WHERE` clause of `DO UPDATE` decides whether
the conflicting row is changed. Because the stored `updated_at` is updated together with the
data, the next comparison always uses the newest version, so a batch with v2, v3, v1 ends with
v3, whatever the order.

`cursor.rowcount` after `executemany` is the total number of rows inserted or updated; rows the
`WHERE` skipped are not counted. `with conn:` commits on success and rolls back if any row fails,
so a half-written batch is never left behind.

## Code

```python
import sqlite3

CREATE = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL, updated_at TEXT NOT NULL
)
"""

UPSERT = """
INSERT INTO orders (id, status, amount, updated_at)
VALUES (:id, :status, :amount, :updated_at)
ON CONFLICT (id) DO UPDATE SET
    status = excluded.status, amount = excluded.amount, updated_at = excluded.updated_at
WHERE excluded.updated_at > orders.updated_at
"""


def upsert_if_newer(conn, rows):
    conn.execute(CREATE)
    with conn:
        cursor = conn.executemany(UPSERT, rows)
    return cursor.rowcount
```

## Complexity

O(n log m) for n incoming rows and m stored rows: each row is one primary-key lookup in a B-tree.

## Another way

Do the comparison in Python: `SELECT updated_at FROM orders WHERE id = ?` for each row, then
`INSERT` or `UPDATE` or skip, counting yourself. It gives the same result but costs an extra
query per row, and two pipelines running at once could both read the old value before either
writes (a race). The single SQL statement makes the check and the write one atomic step.

The comparison is on **text**. That is only correct because every timestamp has the same
fixed format and the same zone (`...Z`). If your source sends mixed offsets, normalise them to
UTC in the transform step before loading.
