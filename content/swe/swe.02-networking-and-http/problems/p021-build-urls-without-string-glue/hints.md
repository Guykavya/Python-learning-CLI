## Hint 1

Which function of `urllib.parse` encodes **one** piece of text so that nothing in it has special meaning? Look at its `safe` parameter: what is the default, and why is that wrong for a segment?

## Hint 2

Encode each segment separately and join the encoded pieces with `/`. For the query, a dict with list values needs one extra argument of `urlencode`.

## Hint 3

```text
url = base.rstrip("/")
for s in segments: url += "/" + quote(str(s), safe="")
pairs = {k: v for k, v in query.items() if v is not None}
qs = urlencode(pairs, doseq=True)
if qs: url += "?" + qs
```
