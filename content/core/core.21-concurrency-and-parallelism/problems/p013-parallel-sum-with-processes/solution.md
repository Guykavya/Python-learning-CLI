## Approach

**Chunking.** `divmod(n, k)` gives a base size and a remainder `extra`. The first `extra`
chunks get one more item, so sizes differ by at most 1 and the bigger ones come first. Using
`min(k, n)` chunks avoids empty ranges when there are fewer items than workers.

**Pool.** `ProcessPoolExecutor` starts worker processes. `pool.map(fn, chunks)` sends each
chunk to a worker and returns the results **in input order**. Adding the partial sums gives the
total. `with` shuts the pool down (and waits for the processes) at the end.

What crosses the process boundary is **pickled**: the function by name (`solution.sum_squares`;
the worker imports `solution` and looks it up) and each `range`. Ranges pickle to three numbers,
which is why we send ranges and not lists of a million ints.

`max_workers=len(chunks)` uses no more processes than there is work.

## Code

```python
from concurrent.futures import ProcessPoolExecutor


def sum_squares(r):
    return sum(i * i for i in r)


def chunk_ranges(n, k):
    k = min(k, n)
    if k <= 0:
        return []
    size, extra = divmod(n, k)
    chunks, start = [], 0
    for i in range(k):
        stop = start + size + (1 if i < extra else 0)
        chunks.append(range(start, stop))
        start = stop
    return chunks


def parallel_sum_squares(n, workers):
    chunks = chunk_ranges(n, workers)
    if not chunks:
        return 0
    with ProcessPoolExecutor(max_workers=len(chunks)) as pool:
        return sum(pool.map(sum_squares, chunks))
```

## Complexity

O(n) work in total, split over `k` processes, so about O(n / k) wall time on `k` free cores,
**plus** the cost of starting processes (tens to hundreds of milliseconds). For small `n` the
plain `sum` is faster: measure before you parallelise. Memory O(k) for the chunks.

## Another way

- The formula `(n - 1) * n * (2n - 1) // 6` gives the answer in O(1). The point here is the
  pattern (chunk, map, combine), which works for any per-item CPU work, like checking primes or
  hashing files.
- `pool.submit(sum_squares, r)` for each chunk and `sum(f.result() for f in futures)` does the
  same with futures. `multiprocessing.Pool().map` is the older API with the same idea.
- `pool.map(fn, items, chunksize=1000)` can do the chunking for you when you pass single
  items, but then each item is still pickled separately.
