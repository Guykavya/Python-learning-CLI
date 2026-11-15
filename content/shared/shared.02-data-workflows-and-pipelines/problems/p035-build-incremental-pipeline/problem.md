# Build: the Pagebound incremental pipeline

This is the module project. You build, in one file, the pipeline the whole chapter has been
preparing: it pulls orders from the Pagebound Orders API, cleans and checks them, loads them into
SQLite and publishes a partitioned Parquet copy. It must be safe to **re-run**, able to **resume**
after a crash, and it must never crash because of one bad record or leak a customer's email.

Take your time: build it piece by piece (the starter suggests an order) and run the tests often.
The test names tell you which part each one checks.

## The API (the tests run a fake one, offline)

```
GET https://api.pagebound.test/v1/orders?limit=3[&updated_since=<ts>][&cursor=<c>]
-> {"items": [order, ...], "next_cursor": "<opaque string>" or null}
```

- Records come sorted by `(updated_at, id)`. With `updated_since`, the API returns only records
  whose `updated_at` is **greater than or equal** (`>=`) to it, so the boundary records come back again.
- `next_cursor` is opaque: just send it back as `cursor`. `null` means this was the last page.
- Send `limit` (the `limit` argument of `run_pipeline`) on every request. The first page of a run
  has no `cursor`. A run without a watermark sends no `updated_since`.
- An order looks like the default Pagebound record (the fixtures `orders_v1.json` and
  `orders_v2.json` are two days of the server's data, served in pages by the tests):

```json
{"id": 101, "customer": {"email": "asha@example.com", "city": "Pune"}, "status": "shipped",
 "amount": "19.99", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
 "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 2}]}
```

## 1. `transform(record, secret) -> dict` and `BadRecord`

Check the fields **in this order** and raise `BadRecord(field, message)` (given in the starter; it
subclasses `ValueError` and has a `.field`) for the first one that is wrong:

| field | valid when | clean value |
|---|---|---|
| `record` | the record is a dict | |
| `id` | an `int` (not `bool`) > 0 | `id` |
| `email` | `customer` is a dict and `customer["email"]` is a str; after `strip()` it has a non-empty part before and after its last `@` | `customer_key` = first 16 hex chars of HMAC-SHA256(`secret`, email stripped and lower-cased) |
| `city` | `customer.get("city")` is `None` or a str | stripped; `""` becomes `None` |
| `status` | one of `shipped`, `pending`, `cancelled` | as is |
| `amount` | a **str** that `Decimal` parses, finite, >= 0, at most 2 decimal places | `amount_cents` (int) |
| `currency` | a 3-letter upper-case str | as is |
| `created_at`, `updated_at` | a str that `datetime.fromisoformat` parses, **with** a time zone | UTC text `YYYY-MM-DDTHH:MM:SSZ` |
| `items` | a list of dicts, each with an `int` `qty` >= 1 (an empty list is fine) | `item_qty` = sum of `qty` |

The clean row has exactly the keys `id, customer_key, city, status, amount_cents, currency,
created_at, updated_at, item_qty`. No email anywhere. (Because every timestamp has the same
UTC text format, comparing the strings compares the instants.)

## 2. Storage

Everything lives in `out_dir` (create it if needed):

- `out_dir/warehouse.db`, SQLite with three tables (create them if missing):
  - `orders(id INTEGER PRIMARY KEY, customer_key TEXT NOT NULL, city TEXT, status TEXT NOT NULL,
    amount_cents INTEGER NOT NULL, currency TEXT NOT NULL, created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL, item_qty INTEGER NOT NULL)`
  - `quarantine(record_id TEXT, updated_at TEXT, field TEXT, reason TEXT, run_id TEXT,
    PRIMARY KEY (record_id, updated_at))`. `record_id` is `json.dumps(record.get("id"))`,
    `updated_at` is `str(record.get("updated_at"))`, `field` is `BadRecord.field`, `reason` is
    `str(error)`. Use `INSERT OR IGNORE`: the same bad record seen again adds nothing. Do **not**
    store the raw record (it contains the email).
  - `state(key TEXT PRIMARY KEY, value TEXT)`: the committed watermark is the row
    `key = 'orders_watermark'`.
- `out_dir/parquet/order_date=YYYY-MM-DD/part-0.parquet`: one file per UTC **created** day.
- `out_dir/checkpoint.json` while a run is unfinished.

**Upsert, only if newer.** For each good record: if the `id` is new, insert it (`inserted`); if
the stored `updated_at` is older, update the whole row (`updated`); otherwise change nothing
(`unchanged`).

**`export_partition(conn, parquet_root, day)`** rewrites `parquet_root/order_date=<day>/part-0.parquet`
from **all** orders in SQLite whose `created_at` starts with `day`, sorted by `id`, with this
schema (no `order_date` column inside the file):

| column | type | | column | type |
|---|---|---|---|---|
| `id` | `int64` not null | | `currency` | `string` not null |
| `customer_key` | `string` | | `created_at` | `timestamp("us", tz="UTC")` not null |
| `city` | `string` | | `updated_at` | `timestamp("us", tz="UTC")` not null |
| `status` | `string` not null | | `item_qty` | `int64` not null |
| `amount` | `decimal128(12, 2)` not null | | | |

Write it atomically: a temporary file in the same folder whose name starts with `.`, then
`os.replace`. The folder must end up containing only `part-0.parquet`.

**Checkpoints.** `save_checkpoint(path, state)` writes the dict as JSON atomically (temp file in
the same folder + `os.replace`); `load_checkpoint(path)` returns the dict, `None` if the file does
not exist, and raises `ValueError` if it is not valid JSON. The state has these keys:

```python
{"run_id": "r1", "since": None or "<watermark used by this run>", "cursor": None or "c3",
 "max_updated_at": None or "<largest updated_at of the good records so far>",
 "days": ["2024-06-01", ...],   # sorted UTC created days of the good records so far
 "fetch_done": False}
```

## 3. `run_pipeline(client, out_dir, secret, run_id, *, limit=3, max_pages=100, max_attempts=4, base_delay=0.5, sleep=time.sleep) -> dict`

1. If `secret` is empty, raise `ValueError` before any request.
2. If `checkpoint.json` exists, **resume** it (use its `since`, `cursor`, `max_updated_at`, `days`,
   `fetch_done`). Otherwise start a new state with `since` = the committed watermark (or `None`).
3. While fetching is not done: if this call has already fetched `max_pages` pages, raise
   `RuntimeError`. Fetch the next page with retries (below). Then, **in one transaction**, transform
   every record: quarantine the bad ones (and log a WARNING that names the order id and the field),
   upsert the good ones, add their created day to `days` and track the largest `updated_at`.
   **After** the commit, save the checkpoint with the page's `next_cursor` (and
   `fetch_done = next_cursor is None`).
4. Call `export_partition(conn, parquet_root, day)` (positional arguments, through the module-level
   name so the tests can replace it) for every day in `days`, in sorted order.
5. Commit the watermark: the larger of the old watermark and `max_updated_at` (it never goes back;
   it stays `None` if nothing was ever loaded). Only now delete the checkpoint.
6. Log one INFO summary line on the logger `"pagebound.pipeline"` that contains `run_id=<run_id>`,
   `loaded=<n>` and `quarantined=<n>`, and return the summary:

```python
{"run_id": "r1", "resumed": False, "pages": 4, "fetched": 10, "loaded": 7, "inserted": 7,
 "updated": 0, "unchanged": 0, "quarantined": 3,
 "partitions": ["2024-06-01", "2024-06-02", "2024-06-03"], "watermark": "2024-06-03T09:00:00Z"}
```

All counts are for **this call** only (`pages` = pages fetched successfully, `loaded` = good
records, `quarantined` = bad records seen). `partitions` = the days exported.

**Retries.** Up to `max_attempts` attempts per page. Retry on `httpx.TransportError`, on 429 and on
5xx. Before retry number *k* (k = 1, 2, ...), call `sleep(base_delay * 2 ** (k - 1))`, except that a
429/5xx response with a numeric `Retry-After` header means `sleep(float(Retry-After))`. Any other
4xx raises `httpx.HTTPStatusError` at once. After the last attempt, raise the last error
(`raise_for_status()` for a status, the transport error itself otherwise).

**Never log** an email, a whole record, or the secret.

## Example

```python
with httpx.Client(base_url="https://api.pagebound.test") as client:
    s1 = run_pipeline(client, "out", secret, "r1")    # 4 pages, loaded 7, quarantined 3
    s2 = run_pipeline(client, "out", secret, "r2")    # 1 page (updated_since=2024-06-03T09:00:00Z),
                                                      # 109 and 110 come back: unchanged 2
```

If run 1 is killed after page 2 was committed but before its checkpoint was written, the next
call resumes from the page-1 checkpoint, fetches page 2 again (its orders are now `unchanged`),
continues with pages 3 and 4, and ends with exactly the same tables and files as a run that never
crashed.
