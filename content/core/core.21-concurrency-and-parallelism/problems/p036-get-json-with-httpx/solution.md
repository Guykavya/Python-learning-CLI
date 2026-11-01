## Approach

`client.get` is a coroutine: awaiting it sends the request and gives back an
`httpx.Response`. httpx, like `requests`, does **not** raise for 404 or 500: a response is a
response. `raise_for_status()` turns 4xx/5xx into an `httpx.HTTPStatusError` that carries the
request and the response. Only then is it safe to treat the body as good data.

## Code

```python
import httpx


async def get_json(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

## Complexity

One request. Time is the network round trip plus O(n) to decode an n-byte body.

## Another way

Check the status yourself:

```python
if response.is_error:            # 4xx or 5xx
    raise RuntimeError(f"{url}: HTTP {response.status_code}")
```

This lets you choose your own error type, but callers that already know httpx expect
`HTTPStatusError`, which also gives them `err.response.status_code` for free. In httpx 0.28
`raise_for_status()` also returns the response, so `return (await client.get(url)).raise_for_status().json()`
works, though the three-line form is easier to read and to debug.
