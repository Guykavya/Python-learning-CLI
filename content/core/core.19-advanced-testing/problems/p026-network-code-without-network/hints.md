## Hint 1

`fetch_title` should not know how bytes travel. What does it need from `http_get`: a status and a text.
Where does the default come from, and why must it be looked up **inside** the function?

## Hint 2

For `default_get` think about what `urlopen` gives back (an object you use in a `with` block, with
`.status` and `.read()`), and what it **raises** for a 404. For `fetch_title`, handle the status first,
then the body.

## Hint 3

```
import json, urllib.request, urllib.error
default_get(url): try: with urllib.request.urlopen(url, timeout=5) as r: return r.status, r.read().decode("utf-8")
                  except urllib.error.HTTPError as e: return e.code, ""
fetch_title(url, http_get=None):
    if http_get is None: http_get = default_get
    status, body = http_get(url)
    if status == 404: return None
    if status != 200: raise RuntimeError(f"HTTP {status} for {url}")
    try: data = json.loads(body) except ValueError: raise ValueError(f"bad JSON from {url}")
    return data["title"]
```
