## Hint 1

For each job write a small table: run number, clock time of the run, attempts after `reserve`, what the handler raises, and what `fail` does. Note that `d`'s `KeyError` is not a `PermanentError`: the worker treats unknown errors as temporary.

## Hint 2

Backoff with rng = 0.5 is `0.75 x min(300, 2 x 2^(attempt-1))`:

```text
attempt 1 -> 0.75 x 2  = 1.5
attempt 2 -> 0.75 x 4  = 3.0
attempt 3 -> 0.75 x 8  = 6.0
attempt 4 -> 0.75 x 16 = 12.0
```

Job `e` runs at t = 0, 1000 and 2000. Job `f` runs at t = 0, 1000, 2000, 3000, 4000; on the 5th attempt `fail` buries it, so `run_at` keeps the value set by the 4th failure.
