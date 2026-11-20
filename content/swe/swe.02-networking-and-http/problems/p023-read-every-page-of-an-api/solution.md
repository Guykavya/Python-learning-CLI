## Approach

```python
from urllib.parse import urljoin


def fetch_all(client, url, max_pages=1000):
    items = []
    seen = set()
    while url is not None:
        if url in seen:
            raise RuntimeError(f"pagination loop: {url} was already fetched")
        if len(seen) >= max_pages:
            raise RuntimeError(f"too many pages (more than {max_pages})")
        seen.add(url)
        response = client.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code} for {url}")
        try:
            data = response.json()
            page_items = data["items"]
        except (ValueError, KeyError, TypeError):
            raise RuntimeError(f"unexpected response body from {url}") from None
        items.extend(page_items)
        nxt = data.get("next")
        url = urljoin(url, nxt) if nxt else None
    return items
```

The loop ends when there is no next page. Two safety nets protect against a faulty or hostile server: the `seen` set (a `next` that points to an earlier page would loop for ever) and `max_pages` (a server that invents a new page forever would fill memory). `urljoin` turns `/items?page=2` into a full URL using the current page's address.

Example: pages `page=1` → `[1, 2, 3]` with `next` page 2; page 2 → `[4, 5]` with `next` page 3; page 3 → `[6, 7]` with `next: null`. The result is `[1, 2, 3, 4, 5, 6, 7]`.

## Complexity

`O(pages + items)`; one request per page.

## Another way

A generator (`yield from page_items`) lets the caller stop early without loading everything. The list version is simpler to test.

## Why it matters

Real APIs paginate everything. A client that stops after the first page silently returns incomplete data; one that follows `next` forever hangs. Both bugs are common.
