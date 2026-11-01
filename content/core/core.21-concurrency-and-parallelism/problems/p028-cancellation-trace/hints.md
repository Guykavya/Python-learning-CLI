## Hint 1

Split the program into three parts and trace each one separately:

1. `p` and `s` until `gather` returns: who is running at each moment, and what does
   `cancel()` change **immediately** (rule 1) and what only **later**?
2. The `asyncio.timeout` block around `slow()`.
3. The `wait_for` around `polite("W")`.

For part 1, ask: when `main` calls `p.cancel()`, where are `P` and `S` paused? Has the
`CancelledError` already been raised there, or will it be raised when they next run?

## Hint 2

Track the ready queue in part 1:

```
create p, s           queue [P, S]            main still running
print done?           -> False
sleep(0)              queue [P, S, main]
P runs to sleep(10)   prints "P: working"
S runs to sleep(10)   prints "S: working"
main: cancel P, S     both return True; P and S are woken -> queue [P, S]
print done?           -> ?  (has P run since the cancel?)
await gather          main waits
P runs: CancelledError at sleep(10) -> except (prints, re-raises) -> finally (prints)
S runs: CancelledError at sleep(10) -> except (prints, swallows) -> return "S result"
```

Then: what does `gather(..., return_exceptions=True)` hold for P and for S? Which of the two
counts as `cancelled()`? What can `cancel()` do to a task that has already finished?

For part 2: does `"after slow"` ever print? What does `slow`'s `finally` print, and in what
order relative to the `except TimeoutError` line?
