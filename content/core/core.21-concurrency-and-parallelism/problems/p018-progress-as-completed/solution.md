## Approach

Two orders are in play, so keep two pieces of information:

- **Completion order** comes from `as_completed`: it yields each future the moment it is done.
- **Submission order** comes from the index. A `Future` does not remember which job it was,
  so build a dictionary `future -> index` while submitting.

Then one loop does both jobs: take the next finished future, look up its index, store the
result in `results[index]` (a list made with the right length up front), and call
`on_done(index, result)`.

Why is `on_done` in the calling thread? `as_completed` is a plain generator running in your
thread; it only *waits* for the workers. Everything inside the `for` loop runs in the thread
that called `run_with_progress`. (A callback added with `future.add_done_callback` would run
in a **worker** thread instead, which is why it is not used here.)

`fut.result()` re-raises the job's exception, so errors propagate with no extra code. The
`with` block then shuts the pool down and waits for the other jobs.

## Code

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_with_progress(funcs, workers, on_done):
    results = [None] * len(funcs)
    if not funcs:
        return results
    with ThreadPoolExecutor(max_workers=workers) as pool:
        index_of = {pool.submit(f): i for i, f in enumerate(funcs)}
        for fut in as_completed(index_of):
            i = index_of[fut]
            results[i] = fut.result()
            on_done(i, results[i])
    return results
```

The `if not funcs` line is not strictly needed (`as_completed` of an empty dict yields
nothing), but it avoids starting a pool for no work.

## Complexity

Wall time is about the time of the slowest "wave" of jobs: with `n` jobs of similar length
`t` and `w` workers, roughly `ceil(n / w) * t`, instead of `n * t` one by one. Extra memory is
O(n) for the futures, the dictionary and the results.

## Another way

Keep the futures in a list and use `wait(futures, return_when=FIRST_COMPLETED)` in a loop,
removing the finished ones each time. It does the same thing with more code;
`as_completed` is that loop packaged for you.

If you only need the results in input order and no progress, `list(pool.map(f, items))` is
simpler still: `map` returns results in input order, but you get nothing until the earlier
items are done.
