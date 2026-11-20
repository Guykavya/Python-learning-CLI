# Read every page of an API

Chapter section 14.3: a list endpoint returns one page at a time:

```json
{"items": [1, 2, 3], "next": "http://api.test/items?page=2"}
```

`next` is the URL of the following page, or `null` on the last page. It may also be a **relative** URL (`"/items?page=2"`). Write

```python
fetch_all(client, url, max_pages=1000)
```

`client` is an `httpx.Client` (the tests use a mock transport). Return the items of all pages, in order, in one list.

- Follow `next` until it is `null` (or missing). Resolve relative links against the URL of the page that gave them (`urllib.parse.urljoin`).
- If a URL would be fetched a **second time** (the server's `next` points back), raise `RuntimeError` with `loop` in the message.
- If more than `max_pages` pages are needed, raise `RuntimeError` mentioning `too many pages`.
- A response with a status other than `200` raises `RuntimeError` whose message contains the status code and the URL.
- A body that is not JSON, or has no `items` list, raises `RuntimeError`.

## Example

```python
fetch_all(client, "http://api.test/items?page=1")    # [1, 2, 3, 4, 5, 6, 7] for three pages
```
