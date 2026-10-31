## Approach

The cache never looks at the real time. It asks `self.clock()` whenever it needs "now", so a test can
supply a list cell or a small `FakeClock` object and move time forward by assigning a number. Each
entry remembers the time it was set; freshness is `now - set_time < ttl`. Re-setting a key stores a new
time, which restarts the lifetime.

## Code

```python
class ExpiringCache:
    def __init__(self, ttl, clock):
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.ttl = ttl
        self.clock = clock
        self._data = {}

    def _alive(self, entry, now):
        return now - entry[1] < self.ttl

    def set(self, key, value):
        self._data[key] = (value, self.clock())

    def get(self, key, default=None):
        entry = self._data.get(key)
        if entry is None or not self._alive(entry, self.clock()):
            return default
        return entry[0]

    def __len__(self):
        now = self.clock()
        return sum(1 for entry in self._data.values() if self._alive(entry, now))
```

## Complexity

`set` and `get` are O(1); `len` is O(n). Expired entries are never deleted here, which is fine for a
test exercise (a real cache would purge them).

## Another way

Pass a `clock` object with a `.now()` method instead of a function, or use the default argument
`clock=time.monotonic` so production code needs no extra wiring.
