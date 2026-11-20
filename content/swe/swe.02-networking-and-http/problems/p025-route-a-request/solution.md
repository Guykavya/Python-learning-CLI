## Approach

```python
import re


def _compile(pattern):
    names = re.findall(r"\{(\w+)\}", pattern)
    regex = re.escape(pattern)
    for name in names:
        regex = regex.replace(re.escape("{" + name + "}"), f"(?P<{name}>[^/]+)")
    return re.compile("^" + regex + "$"), names


def route(routes, method, path):
    method = method.upper()
    patterns = {}
    for (m, pattern), handler in routes.items():
        patterns.setdefault(pattern, {})[m.upper()] = handler
    matches = []
    for pattern, handlers in patterns.items():
        regex, names = _compile(pattern)
        found = regex.match(path)
        if found:
            matches.append((len(names), pattern, handlers, found.groupdict()))
    matches.sort(key=lambda item: item[0])               # fewer parameters = more specific
    for _, pattern, handlers, params in matches:
        wanted = "GET" if method == "HEAD" and "HEAD" not in handlers else method
        if wanted in handlers:
            return 200, handlers[wanted], params
    if matches:
        allowed = sorted({m for _, _, handlers, _ in matches for m in handlers})
        return 405, None, {"Allow": ", ".join(allowed)}
    return 404, None, {}
```

Two steps that people forget: **escaping** the fixed text (a `.` in a pattern such as `/files/{name}.txt` must match only a dot), and **anchoring** (`^...$`, else `/notes/7/extra` would match `/notes/{id}`). `[^/]+` makes a parameter one segment. The 405 branch is only reached when the path is known: that is the difference between "no such page" and "page exists, wrong method", and the `Allow` header is how the server tells the client which methods work (RFC requirement for a 405).

Example: `route(routes, "DELETE", "/notes")`: the pattern `/notes` matches; its handlers are `GET` and `POST`; no `DELETE`: `(405, None, {"Allow": "GET, POST"})`.

## Complexity

`O(patterns)` per request (compile once per request here; real routers precompile).

## Another way

Flask and FastAPI routers do exactly this with converters (`<int:id>`). A trie of path segments makes it faster for thousands of routes.

## Why it matters

Returning `404` for a wrong method hides bugs and confuses clients; `405` with `Allow` tells them exactly what is possible.
