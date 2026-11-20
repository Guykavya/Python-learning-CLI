## Hint 1

What must you remember about each URL? Think of three things: the body, the validator (the ETag) and the time until which the copy is fresh.

## Hint 2

The order of decisions in `get`: (1) is there a fresh copy? return it; (2) otherwise build the request, adding `If-None-Match` when you have an ETag; (3) look at the answer: `304` or something else?

## Hint 3

```text
entry = cache.get(url); now = clock()
if entry and now < entry.fresh_until: return entry.body, "cache"
headers = {"If-None-Match": entry.etag} if entry and entry.etag else {}
resp = client.get(url, headers=headers)
304 and entry: entry.fresh_until = now + max_age(resp) (or now); return entry.body, "revalidated"
200 and not no-store and (etag or max_age): store; else drop the old entry
return resp.content, "network"
```
