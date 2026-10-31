## Hint 1

What should happen at the end depends on what was true at the start: write down
`was_tracing = tracemalloc.is_tracing()` before you change anything. What has to be done (and
undone) in each of the two cases?

## Hint 2

Start (or reset the peak), read the starting level, run, read the peak, and clean up in
`finally`.

```
was_tracing = is_tracing()
if not was_tracing: start()
try:
    reset_peak()
    start_current, _ = get_traced_memory()
    fn(*args, **kwargs)
    _, peak = get_traced_memory()
finally:
    if not was_tracing: stop()
return max(0, peak - start_current)
```
