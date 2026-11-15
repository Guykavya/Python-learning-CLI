# get_json: one safe API call

Every extract step in this module starts with the same three moves: send a GET request, make
sure the server said "OK", and turn the body into Python data. If you write those three moves
once, carefully, every later function can call them and never think about it again.

The fake **Pagebound Orders API** lives at `https://api.pagebound.test`. The tests build the
client for you, with that `base_url` and an `httpx.MockTransport`, so no real network is used.

Write

```python
def get_json(client, path, params=None):
```

- Send `GET path` with `client.get`, passing `params` as the query parameters
  (`params=None` means no query string at all).
- Call `raise_for_status()` **before** looking at the body. A 4xx or 5xx answer must raise
  `httpx.HTTPStatusError`, even when the body is an HTML error page.
- If the status is **204 No Content**, return `None` (there is no body to parse).
- Otherwise parse the body as JSON and return it (a dict, a list, whatever the JSON is).
- If the body is **not valid JSON** (for example an HTML page from a proxy that answers 200),
  raise `NotJSONError`, which is already defined in the starter. Its message must contain the
  `path` and the **first 80 characters** of the body (not more, so a 2 MB HTML page does not
  flood your logs). Use `raise NotJSONError(...) from error` so the original parse error is
  kept as `__cause__`.

**Example**

```python
# server answers 200 with {"data": [...], "page": 2, "next_page": 3}
get_json(client, "/v1/orders", {"page": 2, "per_page": 3})
# {'data': [...], 'page': 2, 'next_page': 3}
# the request URL was https://api.pagebound.test/v1/orders?page=2&per_page=3

# server answers 200 with "<html><body>Maintenance</body></html>"
get_json(client, "/v1/orders")
# NotJSONError: /v1/orders did not return JSON (status 200): '<html><body>Maintenance</body></html>'

# server answers 404 with an HTML page
get_json(client, "/v1/nope")
# httpx.HTTPStatusError: Client error '404 Not Found' ...
```

The exact wording of the `NotJSONError` message is up to you, as long as it contains the path
and the start of the body.
