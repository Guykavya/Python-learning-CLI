## Hint 1

Cancellation arrives as an exception, `CancelledError`, thrown in at the `await` where the
task is paused. Which Python statement runs a piece of code no matter how a block is left:
by `return`, by an exception, or by `CancelledError`?

## Hint 2

Put **only** the work inside `try`, and the acquire **before** it. If the cancel hits during
`acquire()`, you never enter the `try`, so `finally` does not run and nothing is released.

```
conn = await pool.acquire()      # outside the try
try:
    return await work(conn)
finally:
    pool.release(conn)           # success, error or cancel
```

There is no `except CancelledError` at all, so the cancellation keeps going after
`finally`.
