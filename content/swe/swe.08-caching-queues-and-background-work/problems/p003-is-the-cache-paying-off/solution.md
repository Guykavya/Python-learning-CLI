## Approach

Count hits and misses (rejecting anything else), then use the average-cost formula from Hint 2.

```python
def hit_ratio(events):
    hits = misses = 0
    for event in events:
        if event == "hit":
            hits += 1
        elif event == "miss":
            misses += 1
        else:
            raise ValueError(f"unknown event {event!r}: expected 'hit' or 'miss'")
    total = hits + misses
    return hits / total if total else 0.0


def mean_latency(ratio, lookup_ms, db_ms):
    if not 0.0 <= ratio <= 1.0:
        raise ValueError(f"ratio must be between 0 and 1, got {ratio}")
    return lookup_ms + (1.0 - ratio) * db_ms


def break_even_ratio(lookup_ms, db_ms):
    if lookup_ms >= db_ms:
        return None
    return lookup_ms / db_ms
```

With a 1 ms Redis lookup and a 40 ms query, the cache pays off above a 2.5% hit ratio; at 95% the average is 3 ms. The surprise is the other end: a cache that almost never hits makes every request slower and adds a failure point.

## Complexity

`hit_ratio` is O(n) in the number of events; the other two are O(1).

## Another way

`collections.Counter(events)` counts both kinds in one call; check `set(counts) <= {"hit", "miss"}` for bad values. In production you do not keep a list of events: you keep two counters (Redis `INCR`, or Prometheus counters, chapter 15) and compute the ratio over a time window.
