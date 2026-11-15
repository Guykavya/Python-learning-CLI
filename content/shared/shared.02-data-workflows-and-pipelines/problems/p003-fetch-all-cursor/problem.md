# Cursor pagination

Page numbers break when data changes while you read (an order inserted on page 1 pushes one
order from page 1 onto page 2, and you read it twice). Many APIs therefore use a **cursor**: an
opaque token that means "continue right after the last thing I gave you". *Opaque* means you
must not read it, build it or change it. You only send back exactly what you received.

The Pagebound Orders API (base URL `https://api.pagebound.test`) has a cursor endpoint:

```
GET /v1/orders?limit=3                         (first call: NO cursor parameter at all)
-> {"items": [order, order, order], "next_cursor": "b3JkOjEwMw+/="}
GET /v1/orders?cursor=b3JkOjEwMw%2B%2F%3D&limit=3
-> {"items": [order], "next_cursor": null}
```

Write

```python
def fetch_all_cursor(client, limit=3):
```

- First request: `GET /v1/orders` with only `limit`. Do not send `cursor` at all (not
  `cursor=None`, not `cursor=`: some servers treat an empty cursor as an error).
- Every later request: `limit` plus `cursor` set to exactly the last `next_cursor`.
- Call `raise_for_status()` on every answer.
- Collect the `items` of every answer, in order.
- Stop when `next_cursor` is `None` **or the key is missing** from the answer.
- Pass the parameters with `params=` (a dict). Cursors often contain `+`, `/` and `=`; if you
  glue them into the URL by hand, `+` arrives at the server as a space and the cursor breaks.

**Example**

```
request {limit: 3}                      -> items [101, 102, 103], next_cursor "c1+/="
request {limit: 3, cursor: "c1+/="}     -> items [104, 105],      next_cursor None
fetch_all_cursor(client) -> the 5 orders (2 requests)
```

(Only the order ids are shown; the items are full order dicts.)
