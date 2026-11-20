## Hint 1

You do not know how many pages there are, so use a `while` loop that runs until `next` is empty. What do you keep between iterations?

## Hint 2

To detect a loop, remember the URLs you have already fetched (a `set`). To build the next URL from a relative link, `urljoin(current_url, next)` does the right thing for both absolute and relative links.

## Hint 3

```text
items = []; seen = set()
while url:
    if url in seen: raise RuntimeError("... loop ...")
    if len(seen) >= max_pages: raise RuntimeError("too many pages")
    seen.add(url); response = client.get(url)
    status != 200 -> RuntimeError(f"HTTP {status} for {url}")
    data = response.json(); items += data["items"]; url = urljoin(url, data["next"]) if data.get("next") else None
```
