# Page-number pagination

An API never sends you 50,000 orders in one answer. It sends a **page** and tells you where the
next page is. Your job is to keep asking until the API says there is nothing more.

The Pagebound Orders API (base URL `https://api.pagebound.test`, the tests build the client)
works like this:

```
GET /v1/orders?page=1&per_page=3
-> {"data": [order, order, order], "page": 1, "next_page": 2}
GET /v1/orders?page=2&per_page=3
-> {"data": [order, order], "page": 2, "next_page": null}
```

- `data` is the list of orders on this page.
- `next_page` is the number to ask for next, or `null` (`None` in Python) when this was the last page.

Write

```python
def fetch_all_pages(client, per_page=3):
```

- Start at `page=1`. Send `GET /v1/orders` with the query parameters `page` and `per_page`.
- Call `raise_for_status()` on every answer, so a 4xx/5xx raises `httpx.HTTPStatusError`
  (do not catch it and do not return a half list).
- Add the page's `data` to the result, then ask for the page that `next_page` names.
- Stop when `next_page` is `None`. **This is the only stopping rule.** Do not stop because a
  page is short or empty, and do not compute `page + 1` yourself: the API decides.
- Return all orders in the order the API sent them.

**Example**

Seven orders `101` to `107`, `per_page=3`:

```
request page=1 -> data [101, 102, 103], next_page 2
request page=2 -> data [104, 105, 106], next_page 3
request page=3 -> data [107],           next_page None
fetch_all_pages(client) -> the 7 orders (3 requests)
```

(The orders are full dicts like `{"id": 101, "status": "shipped", ...}`; only the ids are shown.)

The test server counts your requests. A page can be short in the middle of the data (the
server filters out deleted orders after paging), and the last page can be full.
