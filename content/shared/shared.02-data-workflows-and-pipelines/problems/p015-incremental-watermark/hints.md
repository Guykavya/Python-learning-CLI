## Hint 1

Split the run into three small functions: `read_watermark(conn)`, `fetch_changed(client, since,
per_page)` and the load. What should the `params` dict look like when `since` is `None`, and
when it is a timestamp? Which record's `updated_at` becomes the new watermark when the API
sorts by id?

## Hint 2

Fetch everything first, then write everything in one `with conn:` block. If a request fails,
the exception leaves the function before any write, and nothing has changed. If a write fails,
`with conn:` rolls back.

```
since = SELECT value FROM pipeline_state WHERE name = 'orders.updated_at'   (None if no row)
params = {"page": 1, "per_page": per_page}
if since is not None: params["updated_since"] = since
records = []
loop: get, raise_for_status, extend with body["data"], stop when next_page is None, else params["page"] = next_page
with conn:
    upsert every record (id, status, amount, updated_at)
    if records: upsert pipeline_state ('orders.updated_at', max(updated_at))
return len(records)
```
