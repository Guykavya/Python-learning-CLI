# Fetch many URLs, at most N at a time

A link checker has a list of URLs and wants the HTTP status of each one. Asking one by one is
slow; firing all 5,000 requests at once gets you blocked by the server (and can run out of
sockets). The polite middle: **at most `limit` requests in flight** at any moment.

Write `async def fetch_many(client, urls, limit) -> dict[str, int]`:

- send a `GET` for every URL with the given `httpx.AsyncClient`,
- run them concurrently, but never more than `limit` at the same time,
- return a dict `url -> status code`. A 404 or 500 is a **result** here, not an error: do not
  raise for it.

The tests use a fake server (`httpx.MockTransport`) whose handler counts how many requests are
inside it at once, so they can see your peak.

**Example**

```python
urls = [f"https://site.test/page/{i}" for i in range(10)]
urls.append("https://site.test/missing")
statuses = await fetch_many(client, urls, limit=3)
statuses["https://site.test/page/0"]     # 200
statuses["https://site.test/missing"]    # 404
# and the server never saw more than 3 requests at once
```
