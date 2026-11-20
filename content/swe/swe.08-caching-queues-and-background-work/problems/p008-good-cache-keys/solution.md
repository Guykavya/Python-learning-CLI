## Approach

Validate, filter, sort, join, then hash only when needed.

```python
import hashlib

MAX_PARAMS_LENGTH = 64


def cache_key(namespace, version, **params):
    if not isinstance(namespace, str) or not namespace or ":" in namespace or any(c.isspace() for c in namespace):
        raise ValueError(f"bad namespace {namespace!r}: non-empty, no ':' and no whitespace")
    kept = sorted((name, value) for name, value in params.items() if value is not None)
    if not kept:
        return f"{namespace}:v{version}"
    part = "&".join(f"{name}={value}" for name, value in kept)
    if len(part) > MAX_PARAMS_LENGTH or any(c.isspace() for c in part):
        part = "sha256=" + hashlib.sha256(part.encode("utf-8")).hexdigest()
    return f"{namespace}:v{version}:{part}"
```

The key keeps the readable form when it is short and safe (easy to debug with `KEYS search:*`), and becomes a fixed 64-character hash when user text could make it long or strange.

## Complexity

O(p log p) for sorting p parameters, plus O(length) for the hash. Keys are at most `namespace + version + 71` characters.

## Another way

Always hash the params part. Keys are then uniform but unreadable. Another option is `urllib.parse.urlencode(sorted(...))`, which escapes spaces and special characters instead of hashing; the key stays readable but can still be long.
