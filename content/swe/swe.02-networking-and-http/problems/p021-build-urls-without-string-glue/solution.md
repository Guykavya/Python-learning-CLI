## Approach

```python
from urllib.parse import quote, urlencode


def build_url(base, segments, query=None):
    url = base.rstrip("/")
    for segment in segments:
        url += "/" + quote(str(segment), safe="")
    if query:
        pairs = {k: v for k, v in query.items() if v is not None}
        text = urlencode(pairs, doseq=True)
        if text:
            url += "?" + text
    return url
```

`quote` defaults to `safe="/"`, which leaves a slash alone: right for a whole path, wrong for **one segment**, where a slash would start a new segment (and `../` could escape it). With `safe=""` every special character becomes `%XX`. `urlencode(doseq=True)` repeats a key for each item of a list; without it a list is turned into the text `"['a', 'b']"`.

Example: `quote("ça va", safe="")` is `%C3%A7a%20va`; in the query a space becomes `+`.

## Complexity

`O(total length)`.

## Another way

`httpx` and `requests` do this for you (`params={"q": "x y"}`). Still, building path segments is on you, and now you know why.

## Why it matters

URL building bugs are security bugs: a user name such as `../admin` or `x?role=admin` pasted into a URL changes what the request means (path traversal, parameter injection).
