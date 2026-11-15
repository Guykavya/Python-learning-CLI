## Hint 1

Write down the loop of a normal run first (request, write, next cursor). Then mark the three
places a crash can happen: during the request, between the commit and the checkpoint save, and
during the save. For each place, what does the checkpoint say afterwards, what is committed,
and what will the next run request first? Which order of "commit" and "save checkpoint" never
skips a page?

## Hint 2

```
cursor = json.loads(cp.read_text())["cursor"] if cp exists else None
written = 0
loop:
    params = {"limit": limit}; if cursor is not None: params["cursor"] = cursor
    response = client.get("/v1/orders", params=params); raise_for_status
    body = response.json()
    with conn: executemany(UPSERT, rows from body["items"])      # commit this page
    written += number of items
    cursor = body["next_cursor"]
    if cursor is None: break
    save checkpoint {"cursor": cursor}: write <name>.tmp, os.replace(tmp, cp)
delete cp (missing_ok=True); return written
```
