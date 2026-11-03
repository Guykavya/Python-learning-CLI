## Approach

The state is the URL to request next; it starts as `path` and becomes the `rel="next"` URL of
each answer. `response.links` parses the Link header (several comma-separated entries, each
`<url>; rel="..."`), so `response.links.get("next")` is either a dict with a `"url"` key or
`None`.

The guard comes free with a `for` loop: `for page_number in range(1, max_pages + 1)` makes at
most `max_pages` requests. Returning inside the loop means "complete, the last page had no
next link". Falling out of the loop means "I used all my pages and the API still says there is
more", which is exactly when to raise. That gives the right boundary without any `>=` vs `>`
puzzle: `max_pages` pages ending without a next link return normally.

Why raise and not return what we have? The caller cannot tell a partial list from a complete
one. Loading 100 pages of a 10,000-page table and reporting success is a silent data loss. An
exception stops the run, appears in the logs with the URL, and somebody raises the limit or
fixes the API.

## Code

```python
import httpx


class TooManyPagesError(RuntimeError):
    """The API kept sending a next link after max_pages pages."""


def fetch_linked(client, path="/v2/orders", max_pages=100):
    orders = []
    url = path
    for page_number in range(1, max_pages + 1):
        response = client.get(url)
        response.raise_for_status()
        orders.extend(response.json()["orders"])
        next_link = response.links.get("next")
        if next_link is None:
            return orders
        url = next_link["url"]
    raise TooManyPagesError(
        f"more than {max_pages} pages from {path}: the API still sent a next link "
        f"after page {max_pages} (last next URL: {url})"
    )
```

## Complexity

At most `max_pages` requests; O(n) memory for `n` orders.

## Another way

A `while` loop with a counter works too, as long as the check is in the right place:

```python
pages = 0
url = path
while url is not None:
    if pages == max_pages:
        raise TooManyPagesError(f"more than {max_pages} pages")
    response = client.get(url)
    response.raise_for_status()
    pages += 1
    orders.extend(response.json()["orders"])
    link = response.links.get("next")
    url = link["url"] if link else None
```

A second guard real crawlers add: remember the URLs already requested in a `set` and raise if
a `next` link points back to one of them. A loop like `A -> B -> A` would otherwise burn all
`max_pages` requests before failing.
