## Hint 1

`wait(pending, timeout=..., return_when=FIRST_COMPLETED)` returns two sets, `(done,
not_done)`, as soon as **at least one** future in `pending` has finished (or the timeout
passes). If a finished future failed, what should happen to the loop? What is left to wait
for next time? And if `done` comes back **empty**, what does that mean?

## Hint 2

The total `timeout` is a deadline. Compute it once with `time.monotonic()`, and pass the
time that is **left** to each `wait`.

Also: `with ThreadPoolExecutor() as pool:` waits for all jobs when the block ends, so
returning from inside it still waits for the slow mirror. Create the pool without `with`
and shut it down with `wait=False`.

```
pool = ThreadPoolExecutor(max_workers=len(funcs))
pending = {pool.submit(f) for f in funcs}
deadline = now + timeout
try:
    while pending:
        done, pending = wait(pending, timeout=deadline - now, return_when=FIRST_COMPLETED)
        if not done: raise TimeoutError
        for fut in done:
            if fut.exception() is None: return fut.result()
            remember the error
    raise RuntimeError(f"all {n} functions failed") from last_error
finally:
    cancel what is left; pool.shutdown(wait=False, cancel_futures=True)
```
