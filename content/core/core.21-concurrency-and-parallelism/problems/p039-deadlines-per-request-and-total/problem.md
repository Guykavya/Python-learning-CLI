# Two deadlines: per request and for the whole batch

A dashboard page shows data from several services. A slow service must not freeze the page,
so there are **two** time limits:

- `per_request`: one request may take at most this many seconds. A request that is too slow
  shows `"timeout"`.
- `total`: the **whole** call must be finished after at most this many seconds, however many
  requests are still going. Anything not finished by then also shows `"timeout"`.

Write `async def fetch_with_deadlines(client, urls, per_request, total) -> dict`:

- fetch all `urls` concurrently with the given `httpx.AsyncClient`,
- return a dict `url -> response.text`, with `"timeout"` for every url that missed either
  deadline, keys in the same order as `urls`,
- when it returns, **no request may still be running** in the background: unfinished ones must
  be cancelled and finished cancelling.

Use `asyncio.timeout(...)` for both deadlines. (httpx has its own `timeout=` setting, but the
fake transport in the tests ignores it, and it limits only single network operations, not
"this whole thing".)

**Example**

```python
# /fast answers after 0.02 s, /slow after 5 s
await fetch_with_deadlines(client, [".../fast", ".../slow"], per_request=0.2, total=1.0)
# {'.../fast': 'fast body', '.../slow': 'timeout'}      returns after about 0.2 s

# three services of 0.3 s each, but only 0.15 s for everything
await fetch_with_deadlines(client, urls, per_request=1.0, total=0.15)
# every value is 'timeout'                              returns after about 0.15 s
```
