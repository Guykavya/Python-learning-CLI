# Good cache keys

Chapter section 4.2 (key design) and "Try it: key design". A cache key must be **the same** for requests that have the same answer, and **different** for requests whose answers differ. It also must never be huge or contain raw user text that could be abused. Write one function that builds keys by fixed rules.

## What to write

```python
def cache_key(namespace: str, version: int, **params) -> str: ...
```

Rules, in this order:

1. `namespace` must be a non-empty string with no `:` and no whitespace; otherwise raise `ValueError`.
2. Parameters whose value is `None` are **dropped** (an absent filter and `None` mean the same).
3. The remaining parameters are **sorted by name** and written as `name=value` (with `str(value)`), joined by `&`. Call this text the *params part*.
4. If the params part is **longer than 64 characters** or contains **any whitespace**, replace it with `sha256=` followed by the hex SHA-256 of the params part (UTF-8).
5. The key is `"{namespace}:v{version}:{params part}"`, or just `"{namespace}:v{version}"` when there are no parameters left.

## Example

```python
cache_key("search", 2, page=1, sort="price", q="lamp")
# 'search:v2:page=1&q=lamp&sort=price'
cache_key("search", 2, q="lamp", sort="price", page=1)      # the same key: order does not matter
cache_key("search", 2, q="lamp", page=1, sort="price", region=None)   # the same key: None dropped
cache_key("search", 2, q="red lamp", page=1)
# 'search:v2:sha256=' + 64 hex characters   (whitespace in the text)
cache_key("config", 1)                                     # 'config:v1'
```

Why hash instead of removing spaces? Removing would make `"red lamp"` and `"redlamp"` the same key: two different answers would share one entry.
