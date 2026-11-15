## Approach

A **partition** is a slice of the table that is always loaded as a whole, here one
`order_date`. Treating it as the unit of work gives three properties at once:

- **Idempotent.** "Make day D equal to what the source says about day D" has the same result
  whether you run it once or five times.
- **Deletes are handled.** Orders that vanished at the source disappear, which an UPSERT alone
  can never do.
- **Failures are contained.** Each day is its own transaction. A crash leaves finished days
  new, the failing day old, later days untouched, and the next run of the same range repairs
  everything.

The order of operations is what makes "old or new, never a mix" true:

| Step | A failure here leaves the day |
|---|---|
| fetching page k of the day | old (nothing written yet) |
| `DELETE` / `INSERT` inside `with conn:` | old (rolled back) |
| after the commit | new |

Two data details need care. Pages can repeat an order while the data shifts, so the fetch keeps
one entry per id (and the count is the number of distinct orders). And an order can move between
days; its primary key is still taken by the row under the old day, so the insert is an UPSERT that
also rewrites `order_date`.

## Code

```python
from datetime import date, timedelta

UPSERT = """
INSERT INTO orders (id, order_date, status, amount) VALUES (:id, :order_date, :status, :amount)
ON CONFLICT (id) DO UPDATE SET
    order_date = excluded.order_date, status = excluded.status, amount = excluded.amount
"""


def fetch_day(client, day):
    by_id, page = {}, 1
    while page is not None:
        response = client.get("/v1/orders", params={"created_on": day, "page": page})
        response.raise_for_status()
        body = response.json()
        for order in body["data"]:
            by_id[order["id"]] = order
        page = body["next_page"]
    return list(by_id.values())


def days_between(start, end):
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def backfill(client, conn, start, end):
    if start > end:
        raise ValueError(f"start {start} is after end {end}")
    conn.execute(CREATE)
    counts = {}
    for day in days_between(start, end):
        key = day.isoformat()
        orders = fetch_day(client, key)
        rows = [{"id": o["id"], "order_date": key, "status": o["status"], "amount": o["amount"]}
                for o in orders]
        with conn:
            conn.execute("DELETE FROM orders WHERE order_date = ?", (key,))
            conn.executemany(UPSERT, rows)
        counts[key] = len(rows)
    return counts
```

## Complexity

For d days with n orders in total: one request per page, O(n) row writes, and d short
transactions. Memory is O(largest day), because one day is held before it is written. An index
on `order_date` keeps each `DELETE` from scanning the whole table.

## Another way

Load the day into a **staging table** first (`orders_stage`), validate it there (counts, totals,
no NULLs), and then swap it in with `DELETE ...; INSERT INTO orders SELECT ... FROM orders_stage`
inside one transaction. That adds a quality gate before the real table changes. The same
"replace the whole partition" idea is used for files: with hive-style Parquet folders
(`order_date=2024-06-01/`) you write the new folder next to the old one and swap it, which a later
section of this chapter covers.
