## Approach

Keep one piece of state, `page`: the page to ask for next. It starts at `1`. Each answer gives
us two things: the data to keep, and the next value of `page`. When the API sends
`next_page: null`, `page` becomes `None` and the `while page is not None` loop ends. The very
first request is not a special case.

The API, not your code, knows where the data ends. A short page or an empty page is common in
real APIs (the server pages first and filters deleted or hidden rows afterwards), so
`len(data) < per_page` is not a safe stopping rule: it can stop early and lose data, or ask
one page too many when the last page happens to be full. Following the `next_page` number
also works when the API skips page numbers.

`raise_for_status()` on every page matters as much as the loop. If page 2 fails and you return
page 1 only, the pipeline loads a partial batch and reports success.

## Code

```python
import httpx


def fetch_all_pages(client, per_page=3):
    orders = []
    page = 1
    while page is not None:
        response = client.get("/v1/orders", params={"page": page, "per_page": per_page})
        response.raise_for_status()
        body = response.json()
        orders.extend(body["data"])
        page = body["next_page"]
    return orders
```

## Complexity

`P` requests for `P` pages, O(n) time and memory for `n` orders.

## Another way

A generator that `yield`s each page's orders lets the caller process (and checkpoint) one page
at a time instead of holding every order in memory:

```python
def iter_pages(client, per_page=3):
    page = 1
    while page is not None:
        response = client.get("/v1/orders", params={"page": page, "per_page": per_page})
        response.raise_for_status()
        body = response.json()
        yield from body["data"]
        page = body["next_page"]
```

`list(iter_pages(client))` gives the same result. Production code also adds a `max_pages`
safety limit (problem p005), so a buggy API that always sends a `next_page` cannot make your
job run forever.
