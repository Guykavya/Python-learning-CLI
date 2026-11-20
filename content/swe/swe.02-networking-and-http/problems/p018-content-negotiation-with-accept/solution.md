## Approach

```python
def _parse(accept):
    ranges = []
    for part in accept.split(","):
        pieces = [p.strip() for p in part.split(";")]
        media = pieces[0].lower()
        if "/" not in media:
            continue
        q = 1.0
        for param in pieces[1:]:
            name, _, value = param.partition("=")
            if name.strip().lower() == "q":
                try:
                    q = float(value)
                except ValueError:
                    q = 0.0
        ranges.append((media, q))
    return ranges


def _specificity(media_range, offered):
    if media_range == offered:
        return 3
    if media_range.endswith("/*") and media_range[:-1] == offered.split("/")[0] + "/":
        return 2
    if media_range == "*/*":
        return 1
    return 0


def choose(accept_header, offered):
    if not offered:
        return None
    if accept_header is None or not accept_header.strip():
        return offered[0]
    ranges = _parse(accept_header)
    best, best_q = None, 0.0
    for candidate in offered:
        found = (0, 0.0)
        for media, q in ranges:
            spec = _specificity(media, candidate.lower())
            if spec > found[0]:
                found = (spec, q)
        q = found[1]
        if q > best_q:
            best, best_q = candidate, q
    return best
```

The key line is `if spec > found[0]`: only a **more specific** range replaces the earlier match, so `text/html;q=0` overrides `text/*;q=0.8` for `text/html` while `text/plain` still gets `0.8`. The final comparison `q > best_q` is strict, so on equal q-values the first offered type stays chosen (the server's order). A q of 0 never beats the initial `best_q = 0.0`, so unacceptable types are never selected.

Example: `choose("text/*;q=0.8, text/html;q=0", ["text/html", "text/plain"])`: `text/html` matches exactly (score 3, q 0) and also `text/*` (score 2): the exact range wins, q 0. `text/plain` matches only `text/*`: q 0.8. The answer is `text/plain`.

## Complexity

`O(offered * ranges)`.

## Another way

Frameworks such as Flask use `werkzeug.datastructures.MIMEAccept.best_match`. Writing it once shows why `q=0` and specificity matter.

## Why it matters

An API that returns JSON to a browser asking for `text/html`, or ignores `q=0`, is subtly wrong. Correct negotiation lets one URL serve several formats.
