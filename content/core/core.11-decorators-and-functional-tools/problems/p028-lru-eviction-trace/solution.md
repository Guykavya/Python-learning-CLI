## Approach

Track the cache from oldest use to newest use.

| Call | Hit or miss | Cache after (old → new) |
|---|---|---|
| `square(2)` | miss, prints `compute 2` | [2] |
| `square(3)` | miss, prints `compute 3` | [2, 3] |
| `square(2)` | **hit** | [3, 2] |
| `square(4)` | miss, 3 is evicted | [2, 4] |
| `square(3)` | miss, 2 is evicted | [4, 3] |
| `square(2)` | miss, 4 is evicted | [3, 2] |

One hit, five misses, two entries: `CacheInfo(hits=1, misses=5, maxsize=2, currsize=2)`.

`cache_clear()` empties the cache **and** resets the counters. Then `square(4)` is a miss.
`square(n=4)` uses a different key (keyword instead of position), so it is another miss and
computes again. The last `square(4)` finds the positional key: a hit. So:
`CacheInfo(hits=1, misses=2, maxsize=2, currsize=2)`.

## Output

```text
compute 2
4
compute 3
9
4
compute 4
16
compute 3
9
compute 2
4
CacheInfo(hits=1, misses=5, maxsize=2, currsize=2)
compute 4
16
compute 4
16
16
CacheInfo(hits=1, misses=2, maxsize=2, currsize=2)
```

## Complexity

Each lookup is O(1) on average; the order is kept with a linked list inside `lru_cache`.

## Another way

"First in, first out" would throw out the oldest **stored** entry, ignoring reads. Then
`square(4)` would evict 2 (stored first) instead of 3. LRU keeps entries that are used often,
which is usually what you want. Python's documentation says that different argument
patterns, such as `f(4)` and `f(n=4)`, "may" get separate entries: do not rely on them being shared.
