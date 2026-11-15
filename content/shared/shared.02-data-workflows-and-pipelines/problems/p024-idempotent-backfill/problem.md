# Idempotent backfill: replace one day at a time

A bug in the transform step stored wrong amounts for the first days of June. It is fixed, and
now you must **backfill**: reload a range of past days from the Pagebound Orders API. A backfill
is the job people run by hand, often more than once, sometimes over a range that overlaps the
nightly job. It must be **idempotent**: running it for the same range again gives exactly the
same table.

Upserts are not enough here. An order that was **deleted** at the source (a test order, a fraud
cancellation that was purged) would stay in your table forever, because an upsert never removes
anything. The standard tool is **delete + insert per partition**: treat each day as one unit,
and in **one transaction** delete everything you have for that day and insert what the source
has now.

Write

```python
def backfill(client: httpx.Client, conn: sqlite3.Connection, start: date, end: date) -> dict[str, int]:
```

**The API** (page pagination per day):

```
GET /v1/orders?created_on=YYYY-MM-DD&page=<n>
-> {"data": [<order>, ...], "page": n, "next_page": n + 1 or null}
```

A day with no orders answers `{"data": [], "page": 1, "next_page": null}`. Because the data can
shift while you page, **the same order can appear on two pages of one day**: store it once.
Call `raise_for_status()` on every response.

**The table** (create it if missing):

```sql
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, order_date TEXT NOT NULL, status TEXT NOT NULL, amount TEXT NOT NULL
)
```

Store `order_date` = the day you requested (`"2024-06-01"`), and `status` and `amount` exactly
as the API gives them (do not convert them).

**For each day from `start` to `end`, both included, in order:**

1. Fetch **all** pages of that day first. Nothing is written while fetching, so a network error
   in the middle of a day leaves that day's old rows untouched.
2. In **one transaction**: `DELETE` that day's rows, then insert the day's orders. If anything
   fails (the `NOT NULL` constraints reject a broken record, for example), the transaction
   rolls back, so the day keeps its old rows, and the error propagates.
3. An order can **move** to another day (its date was corrected at the source). If its id is
   already stored under a different day, it must end up only under the day being loaded now.

Days before the failing one stay committed; the next run of the same range repairs the rest.
Return `{day as "YYYY-MM-DD": number of orders stored for that day}` in day order.
If `start > end`, raise `ValueError` before sending any request.

Use `datetime.date` and `timedelta(days=1)` to walk the days; `day.isoformat()` gives the string.

**Example**

```python
# table before: (2, '2024-06-01', 'pending', '5.00'), (90, '2024-06-03', 'shipped', '1.00'),
#               (91, '2024-05-31', 'shipped', '2.00')
# API: 06-01 -> page 1 [1, 2], page 2 [3];  06-02 -> page 1 [4, 5], page 2 [5, 6];  06-03 -> no orders
backfill(client, conn, date(2024, 6, 1), date(2024, 6, 3))
# {'2024-06-01': 3, '2024-06-02': 3, '2024-06-03': 0}
# table after: ids 1, 2, 3 (06-01), 4, 5, 6 (06-02), and 91 (05-31, outside the range, untouched).
# Order 2 has its new values; order 90 is gone because 06-03 is now empty at the source.

backfill(client, conn, date(2024, 6, 1), date(2024, 6, 3))   # again: the very same table
```
