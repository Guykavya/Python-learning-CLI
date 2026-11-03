## Approach

The state of the loop is the `params` dict for the next request. It starts as `{"limit": limit}`
(no cursor key, because there is nothing to continue from) and after every answer becomes
`{"limit": limit, "cursor": <the cursor the server just gave>}`. `body.get("next_cursor")`
returns `None` both when the value is `null` and when the key is missing, so one `is None`
check covers both ways an API can say "no more".

Two rules make cursors work. First, a cursor is opaque: send back exactly the string you got.
The test server only knows its own tokens, so a computed cursor gets a 400. Second, let httpx
encode it: `params=` percent-encodes `+`, `/`, `=` and `&`, while a hand-built URL like
`f"/v1/orders?cursor={c}"` sends `+` as a space and lets `&` start a new parameter.

Why do APIs use cursors? The token usually encodes "the last id/timestamp you saw", so the next
answer starts right after it. Inserts and deletes on earlier pages cannot shift the window,
which is exactly the skip/duplicate problem of page and offset pagination.

## Code

```python
import httpx


def fetch_all_cursor(client, limit=3):
    orders = []
    params = {"limit": limit}
    while True:
        response = client.get("/v1/orders", params=params)
        response.raise_for_status()
        body = response.json()
        orders.extend(body["items"])
        cursor = body.get("next_cursor")
        if cursor is None:
            return orders
        params = {"limit": limit, "cursor": cursor}
```

## Complexity

One request per answer; O(n) time and memory for `n` orders.

## Another way

Keep only the cursor as state and build the params each time:

```python
def fetch_all_cursor(client, limit=3):
    orders, cursor = [], None
    while True:
        params = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        response = client.get("/v1/orders", params=params)
        response.raise_for_status()
        body = response.json()
        orders.extend(body["items"])
        cursor = body.get("next_cursor")
        if cursor is None:
            return orders
```

Storing the last cursor is also what makes a run **resumable**: if you save it after each
page, a crashed run can continue from there (problem p019).
