# Incremental load with a watermark in a state table

Downloading every order on every run gets slower each day. An **incremental** load asks only
for what changed since the last run. The pipeline remembers a **watermark** (high-water mark):
the largest `updated_at` it has loaded so far. Next time it asks for `updated_since=<watermark>`.

Write

```python
def run_incremental(client: httpx.Client, conn: sqlite3.Connection, per_page: int = 3) -> int:
```

that loads new and changed orders from the Pagebound Orders API into SQLite and returns how
many records it received in this run.

**The API** (base URL already set on `client`):

```
GET /v1/orders?page=<n>&per_page=<k>[&updated_since=<timestamp>]
-> {"data": [<order>, ...], "page": n, "next_page": n + 1 or null}
```

- Without `updated_since` it returns every order. With it, it returns only orders whose
  `updated_at` is **strictly greater** (`>`) than the value.
- Orders come **sorted by id, not by time**. Do not assume the last record is the newest.
- An order looks like the default Pagebound record (`id`, `customer`, `status`, `amount`,
  `currency`, `created_at`, `updated_at`, `items`). All timestamps are UTC in the fixed format
  `YYYY-MM-DDTHH:MM:SSZ`, so they compare correctly as text.
- Call `response.raise_for_status()` on every response.

**The database.** Create both tables if they do not exist:

```sql
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pipeline_state (name TEXT PRIMARY KEY, value TEXT NOT NULL);
```

The watermark lives in `pipeline_state` in the row with `name = 'orders.updated_at'`.

**Each run must:**

1. Read the watermark. If there is none (first run), send **no** `updated_since` parameter at all.
2. Fetch every page (start at `page=1`, always send `per_page`, follow `next_page` until it is null).
3. Upsert the orders (`id`, `status`, `amount`, `updated_at`) so a changed order replaces its old row.
4. Set the watermark to the **largest** `updated_at` received. If nothing was received, leave
   it as it was (on a first run with no data, there is still no watermark row).
5. Do steps 3 and 4 in **one transaction**: if the run fails anywhere, neither the orders nor the
   watermark may change, and the exception must propagate to the caller.

**Example**

```python
# the API holds 101..105; the newest updated_at is 103's "2024-06-03T09:00:00Z"
run_incremental(client, conn)      # 5   requests: page=1, page=2 (no updated_since)
run_incremental(client, conn)      # 0   one request: page=1&per_page=3&updated_since=2024-06-03T09:00:00Z
# order 102 is changed and order 106 is added on the server
run_incremental(client, conn)      # 2
conn.execute("SELECT value FROM pipeline_state WHERE name = 'orders.updated_at'").fetchone()
# ('2024-06-04T10:00:00Z',)        # 102's new updated_at, the largest seen
```
