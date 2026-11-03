# Resume a cursor fetch from a checkpoint

A full extract of the Pagebound Orders API takes hours in real life. If it dies on page 900,
starting again from page 1 wastes all that work. Instead the pipeline writes a **checkpoint**
after every page and, when it is started again, **resumes** from there.

Write

```python
def fetch_resumable(client: httpx.Client, conn: sqlite3.Connection, checkpoint_path, limit: int = 3) -> int:
```

**The API** (cursor pagination, base URL already set on `client`):

```
GET /v1/orders?limit=<k>[&cursor=<c>]
-> {"items": [<order>, ...], "next_cursor": "<opaque string>" or null}
```

The first request has **no** `cursor` parameter. Each response's `next_cursor` is the value to
send next; `null` means this was the last page. Cursors are opaque: never build or parse them,
only pass back what the server gave you. Call `raise_for_status()` on every response.

**The table** (create it if missing; store only these columns):

```sql
CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL, updated_at TEXT NOT NULL)
```

**The checkpoint** is a JSON file at `checkpoint_path` holding `{"cursor": "<next cursor>"}`.

**What a run does**

1. If the checkpoint file exists, read its cursor and start with that request. Otherwise start
   from the beginning (no cursor).
2. For every page, in this order:
   1. **upsert** its orders (`INSERT ... ON CONFLICT (id) DO UPDATE`), then **commit**;
   2. if `next_cursor` is not null, **save** the checkpoint `{"cursor": next_cursor}` atomically
      (temp file in the same folder + `os.replace`, as in p018; call it as `os.replace` because
      the tests make it fail on purpose).
3. After the last page, **delete** the checkpoint file, so the next run is a fresh full run.
4. Return the number of orders written by **this** call.
5. Do not catch errors: if a request fails, the exception propagates. That is the "crash".

Why data first and checkpoint second? If the process dies between the two steps, the
checkpoint is one page behind: the resume fetches that page again and the upsert writes the
same rows again, so nothing is lost and nothing is duplicated. The other order could lose a page.

**Example** (8 orders, `limit=3`; the cursors shown are made up, yours will differ)

```python
fetch_resumable(client, conn, "state/cp.json")
# request 1: limit=3                 -> 3 orders, next_cursor "q8Zt"   (committed, checkpoint saved)
# request 2: limit=3&cursor=q8Zt     -> 3 orders, next_cursor "m2Kd"   (committed, checkpoint saved)
# request 3: limit=3&cursor=m2Kd     -> ConnectError: the run crashes
# state/cp.json now holds {"cursor": "m2Kd"}; the table has 6 orders

fetch_resumable(client, new_conn, "state/cp.json")    # 2
# request 4: limit=3&cursor=m2Kd     -> 2 orders, next_cursor null; cp.json is deleted
```
