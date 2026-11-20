# Is the cache paying off?

Chapter sections 2.1 (hits, misses and the hit ratio) and 4.3 (what to measure). A cache is not free: **every** request first asks the cache, which takes time, and a miss then also goes to the database. A cache with a low hit ratio makes the average request *slower*. Write three small functions that answer "is it worth it?".

## What to write

```python
def hit_ratio(events: list[str]) -> float: ...
def mean_latency(ratio: float, lookup_ms: float, db_ms: float) -> float: ...
def break_even_ratio(lookup_ms: float, db_ms: float) -> float | None: ...
```

- `hit_ratio(events)`: `events` is a list of the strings `"hit"` and `"miss"`. Return hits / (hits + misses). An empty list gives `0.0`. Any other string raises `ValueError` naming it.
- `mean_latency(ratio, lookup_ms, db_ms)`: the average time of one request **with** the cache. Every request pays `lookup_ms`; a miss (a fraction `1 - ratio` of requests) also pays `db_ms`. Raise `ValueError` if `ratio` is outside 0..1.
- `break_even_ratio(lookup_ms, db_ms)`: the hit ratio at which the cache is exactly as fast as going straight to the database (which costs `db_ms` per request). Above it the cache helps. If `lookup_ms >= db_ms` no ratio can help, so return `None`.

## Example

```python
hit_ratio(["hit", "hit", "miss", "hit"])   # 0.75
mean_latency(0.75, 1, 40)                  # 1 + 0.25 * 40 = 11.0 ms   (without a cache: 40 ms)
mean_latency(0.0, 1, 40)                   # 41.0 ms: a useless cache is slower than no cache
break_even_ratio(1, 40)                    # 0.025: above a 2.5% hit ratio the cache pays off
break_even_ratio(5, 5)                     # None
```

Work out `break_even_ratio` on paper first: set `mean_latency(r, lookup, db)` equal to `db` and solve for `r`.
