# Testing time: an injected clock

Code that calls `time.time()` directly is hard to test: you would have to wait. If the **clock is a
parameter**, a test can use a fake clock and move time by hand, instantly.

In `solution.py` write `class ExpiringCache`:

```python
class ExpiringCache:
    def __init__(self, ttl, clock): ...
    def set(self, key, value): ...
    def get(self, key, default=None): ...
    def __len__(self): ...
```

- `clock` is a function with no arguments that returns the current time in seconds (a number). Call it
  **only when needed**, never `time.time()` yourself.
- `ttl` is the lifetime in seconds. An entry set at time `t` is valid while `now - t < ttl`; at
  `now - t >= ttl` it has **expired** (the border belongs to "expired").
- `get(key, default)` returns the value, or `default` for a missing or expired key.
- `set` on an existing key replaces the value **and restarts** its lifetime.
- `len(cache)` counts only entries that have not expired.
- `ttl <= 0` raises `ValueError`.

**Example**

```python
now = [100.0]
cache = ExpiringCache(ttl=10, clock=lambda: now[0])
cache.set("a", 1)
now[0] = 109.9
cache.get("a")     # 1
now[0] = 110.0
cache.get("a")     # None   (expired exactly at the border)
```
