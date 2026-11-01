## Hint 1

`as_completed(futures)` yields each future as soon as it is done, but a future does not
know its own position in `funcs`. Where can you keep "this future belongs to job number i"
so you can look it up when the future comes out of `as_completed`?

## Hint 2

A dictionary from future to index does it. And because the loop over `as_completed` runs in
**your** thread, calling `on_done` inside that loop already satisfies the "calling thread"
rule.

```
results = [None] * len(funcs)
with ThreadPoolExecutor(max_workers=workers) as pool:
    index_of = {pool.submit(f): i for i, f in enumerate(funcs)}
    for fut in as_completed(index_of):
        i = index_of[fut]
        results[i] = fut.result()      # re-raises if the job failed
        on_done(i, results[i])
return results
```
