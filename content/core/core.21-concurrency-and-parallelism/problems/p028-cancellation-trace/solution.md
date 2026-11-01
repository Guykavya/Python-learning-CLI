## Approach

Trace with a ready queue, and remember that `cancel()` only *requests*: the
`CancelledError` is raised later, inside the task, at the `await` where it is paused.

### Part 1: two tasks, one polite and one stubborn

| Step | Running | What happens | Queue after | Printed |
|---|---|---|---|---|
| 1 | main | `create_task` twice: P and S are queued, not started | `[P, S]` | |
| 2 | main | `p.done()`: P has not even started | `[P, S]` | `P done before it ran? False` |
| 3 | main | `await sleep(0)`: main goes to the back | `[P, S, main]` | |
| 4 | P | enters `try`, prints, pauses in `sleep(10)` | `[S, main]` | `P: working` |
| 5 | S | enters `try`, prints, pauses in `sleep(10)` | `[main]` | `S: working` |
| 6 | main | `p.cancel()`: request accepted, P is woken to receive it | `[P]` | `cancel P: True` |
| 7 | main | `s.cancel()`: same for S | `[P, S]` | `cancel S: True` |
| 8 | main | `p.done()`: P has **not run** since the request, so it is still pending | `[P, S]` | `P done right after cancel? False` |
| 9 | main | `await gather(p, s, return_exceptions=True)`: main waits for both | `[P, S]` | |
| 10 | P | `CancelledError` raised at `sleep(10)`; the `except` matches | | `P: cancelled, cleaning up` |
| 11 | P | bare `raise` re-raises; `finally` runs on the way out | | `P: finally` |
| 12 | P | the error escapes: P ends **cancelled** (`"P: finished"` never prints) | `[S]` | |
| 13 | S | `CancelledError` at `sleep(10)`; the `except` prints and does **not** re-raise | | `S: cancelled, but I swallow it` |
| 14 | S | continues after the `try` and returns normally: the cancel was swallowed | `[main]` | |
| 15 | main | gather's results: P's slot holds a `CancelledError` object, S's holds its return value | | `results: ['CancelledError', 'S result']` |
| 16 | main | P ended by the error, S ended by `return` | | `P cancelled? True \| S cancelled? False` |
| 17 | main | `cancel()` on a finished task does nothing and returns `False` | | `cancel P again: False` |

### Part 2: `asyncio.timeout` around `slow()`

| Step | What happens | Printed |
|---|---|---|
| 18 | the timeout block starts a 0.05 s alarm; `slow()` pauses in `sleep(10)` | |
| 19 | 0.05 s later the alarm cancels **main** (the task running the block) at that `await` | |
| 20 | the `CancelledError` goes up through `slow`: its `finally` runs | `slow: finally` |
| 21 | `"after slow"` is skipped: the exception passes it | |
| 22 | the `CancelledError` reaches the end of the `async with`; the timeout turns it into `TimeoutError` | |
| 23 | the outer `except TimeoutError` catches it | `main: TimeoutError from asyncio.timeout` |

### Part 3: `wait_for` around a polite coroutine

| Step | What happens | Printed |
|---|---|---|
| 24 | `polite("W")` starts and pauses in `sleep(10)` | `W: working` |
| 25 | after 0.05 s `wait_for` cancels it; `except CancelledError` runs and re-raises | `W: cancelled, cleaning up` |
| 26 | `finally` runs | `W: finally` |
| 27 | `wait_for` turns the cancel into `TimeoutError`, caught by `main` | `main: wait_for raised TimeoutError` |
| 28 | | `main: end` |

### Lessons

- `cancel()` is a request (steps 6 to 8). Code right after `cancel()` must not assume the task
  has stopped; `await` it to be sure.
- The `except CancelledError: ... raise` plus `finally` pattern (P, W) cleans up **and**
  keeps the cancel. The swallowing pattern (S) silently turns a cancel into a normal return:
  `s.cancelled()` is `False`, and anything waiting for S to stop (a `TaskGroup`, a timeout, a
  shutdown) is fooled.
- Timeouts are built on cancellation (part 2 and 3). That is why swallowing `CancelledError`
  also breaks timeouts: `asyncio.timeout` only raises `TimeoutError` if the cancel comes back
  out of the block.

## Output

```text
P done before it ran? False
P: working
S: working
cancel P: True
cancel S: True
P done right after cancel? False
P: cancelled, cleaning up
P: finally
S: cancelled, but I swallow it
results: ['CancelledError', 'S result']
P cancelled? True | S cancelled? False
cancel P again: False
slow: finally
main: TimeoutError from asyncio.timeout
W: working
W: cancelled, cleaning up
W: finally
main: wait_for raised TimeoutError
main: end
```

## Complexity

Not relevant for a trace. The program runs in about 0.1 s: two 0.05 s timeouts; nothing
waits for the 10-second sleeps.

## Another way

Check your answer by experiment: add `print(p.cancelling())` right after `p.cancel()` (it
shows `1`, the number of pending cancel requests), or change S's handler to re-raise and
predict how output lines 10 and 11 change (`results` becomes
`['CancelledError', 'CancelledError']`, and `S cancelled?` becomes `True`).
