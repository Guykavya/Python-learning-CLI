## Hint 1

`chunk_ranges` is plain arithmetic. With `n = 10, k = 3`, `divmod(10, 3)` is `(3, 1)`: every
chunk gets 3, and the first **1** chunk gets one extra. What should `k` become when `n < k`?

## Hint 2

```
chunk_ranges(n, k):
    k = min(k, n); if k == 0: return []
    size, extra = divmod(n, k)
    start = 0
    for i in 0..k-1:
        stop = start + size + (1 if i < extra else 0)
        add range(start, stop); start = stop

parallel_sum_squares(n, workers):
    chunks = chunk_ranges(n, workers)
    if no chunks: return 0
    with ProcessPoolExecutor(max_workers=len(chunks)) as pool:
        return sum(pool.map(sum_squares, chunks))
```

## Hint 3

`pool.map(sum_squares, chunks)` pickles `sum_squares` (by its module and name) and each
`range` object, sends them to the workers, and gives back the results in chunk order. A
lambda or a function defined inside `parallel_sum_squares` cannot be pickled that way.
