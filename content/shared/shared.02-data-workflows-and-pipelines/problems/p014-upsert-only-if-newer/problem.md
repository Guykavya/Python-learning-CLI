# Upsert only if the incoming row is newer

A plain `INSERT` duplicates rows when a batch is loaded twice. A plain "insert or replace"
has the opposite problem: if an **old** version of an order arrives after a newer one (a
retried page, an overlap window, a backfill of last week), it overwrites the newer data.

The safe write is an **UPSERT that only wins when it is newer**: insert new ids, update an
existing id only when the incoming `updated_at` is strictly later than the stored one.

Write

```python
def upsert_if_newer(conn: sqlite3.Connection, rows: list[dict]) -> int:
```

- Create the table if it does not exist, with exactly this schema:

  ```sql
  CREATE TABLE IF NOT EXISTS orders (
      id         INTEGER PRIMARY KEY,
      status     TEXT NOT NULL,
      amount     TEXT NOT NULL,
      updated_at TEXT NOT NULL
  )
  ```

- Each row is a dict with keys `id`, `status`, `amount` (a string such as `"19.99"`) and
  `updated_at`. All timestamps in this problem are UTC in the same fixed format
  `YYYY-MM-DDTHH:MM:SSZ`, so comparing them as **text** gives the right time order (this is why
  pipelines normalise timestamps before they load them).
- New id: insert it. Existing id: overwrite `status`, `amount` and `updated_at` **only if** the
  incoming `updated_at` is greater than the stored one. Equal timestamps mean "the same
  version": keep the stored row.
- Rows inside one batch can repeat an id, in any order; the newest version must end up in the table.
- Commit before returning, and return how many rows were **inserted or actually updated**
  (ignored stale rows do not count). Use query parameters (`?` or `:name`), never f-strings.

**Example**

```python
conn = sqlite3.connect(":memory:")
upsert_if_newer(conn, [
    {"id": 101, "status": "pending", "amount": "19.99", "updated_at": "2024-06-01T10:00:00Z"},
    {"id": 102, "status": "pending", "amount": "5.00",  "updated_at": "2024-06-01T10:00:00Z"},
])                                       # 2  (two inserts)
upsert_if_newer(conn, [
    {"id": 101, "status": "shipped", "amount": "19.99", "updated_at": "2024-06-01T12:00:00Z"},  # newer
    {"id": 102, "status": "cancelled", "amount": "5.00", "updated_at": "2024-06-01T09:00:00Z"}, # stale
])                                       # 1  (only 101 changed)
conn.execute("SELECT id, status FROM orders ORDER BY id").fetchall()
# [(101, 'shipped'), (102, 'pending')]
```
