## Hint 1

What does `await client.get(url)` give you back? Look at the `httpx.Response` object: which
method raises an error for a bad status, and which one decodes the body as JSON? Does httpx
raise by itself when the server answers 404?

## Hint 2

```
response = await client.get(url)
response.raise_for_status()      # raises httpx.HTTPStatusError for 4xx and 5xx
return response.json()
```
