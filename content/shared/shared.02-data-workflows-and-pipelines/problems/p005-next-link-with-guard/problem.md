# Follow the Link header, with a page guard

Some APIs do not put the next page in the body at all. They send an HTTP **Link header** with a
ready-made URL (GitHub's API does this):

```
Link: <https://api.pagebound.test/v1/orders?page=1>; rel="first", <https://api.pagebound.test/v1/orders?after=Zm9v>; rel="next"
```

The entry with `rel="next"` is the URL of the next page. When there is no `next` entry, you are
on the last page. httpx parses this header for you: `response.links` is a dict such as
`{"first": {"url": "...", "rel": "first"}, "next": {"url": "...", "rel": "next"}}`.

APIs have bugs. One that always sends a `next` link would make a naive loop run forever,
eating memory and hammering the server. Production code therefore has a **safety limit**.

The Pagebound API's v2 endpoint works like this (base URL `https://api.pagebound.test`):

```
GET /v2/orders
-> body {"orders": [order, ...]}   header Link: <...?after=abc>; rel="next"   (or no next link)
```

The next URL may be absolute (`https://api.pagebound.test/v2/orders?after=abc`) or a path
(`/v2/orders?after=abc`). Request it exactly as given; the client's `base_url` handles paths.

Write

```python
class TooManyPagesError(RuntimeError): ...       # already in the starter

def fetch_linked(client, path="/v2/orders", max_pages=100):
```

- Request `path`, then keep requesting the `rel="next"` URL of the last answer until an answer
  has no `next` link. Call `raise_for_status()` on every answer.
- Collect the `orders` of every page in order and return them.
- Request **at most `max_pages` pages**. If page number `max_pages` still has a `next` link,
  raise `TooManyPagesError` without making another request. Its message must contain the
  number `max_pages`. Do not return the partial list: a pipeline that silently loads part of
  the data is worse than one that fails loudly.
- Exactly `max_pages` pages, the last with no `next` link, is fine (not an error).

**Example**

```
GET /v2/orders            -> orders [101, 102], next /v2/orders?after=t1
GET /v2/orders?after=t1   -> orders [103],      no next link
fetch_linked(client)                      -> the 3 orders (2 requests)
fetch_linked(client, max_pages=1)         -> TooManyPagesError: more than 1 pages ... (1 request)
fetch_linked(endless_client, max_pages=5) -> TooManyPagesError after exactly 5 requests
```
