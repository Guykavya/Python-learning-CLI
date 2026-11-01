# GET JSON with httpx

Write `async def get_json(client, url)`:

- send a `GET` request to `url` with the **given** `client` (an `httpx.AsyncClient`),
- if the status is 4xx or 5xx, raise `httpx.HTTPStatusError` (one method call does this),
- otherwise return the decoded JSON body (usually a `dict`).

Do not create a client inside the function. Making one client and passing it around is how
real programs reuse connections, and it lets the tests hand you a fake one.

The tests never touch the network. They build the client like this:

```python
def handler(request):
    if request.url.path == "/users/1":
        return httpx.Response(200, json={"id": 1, "name": "Asha"})
    return httpx.Response(404, json={"error": "not found"})

async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
    ...
```

**Example**

```python
await get_json(client, "https://api.example.com/users/1")
# {'id': 1, 'name': 'Asha'}

await get_json(client, "https://api.example.com/users/99")
# httpx.HTTPStatusError: Client error '404 Not Found' for url '...'
```
