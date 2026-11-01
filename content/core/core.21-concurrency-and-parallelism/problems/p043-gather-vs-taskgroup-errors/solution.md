## Approach

Follow the clock (times in seconds from the start of each part).

**Part 1, plain `gather`**

| Time | Event | Printed |
|---|---|---|
| 0 | | `-- gather` |
| 0.01 | `a` succeeds | `a done` |
| 0.02 | `b` raises `ValueError('b')`; `gather` passes it to `main` **now** | `caught ValueError('b')` |
| | `c` is **not** cancelled; it is still sleeping | |
| 0.03 | `c` succeeds, in the background | `c done` |
| 0.07 | the 0.05 s sleep (started at 0.02) ends | `gather over` |

`gather` stopped *waiting*, not *running*. If `main` had returned instead of sleeping, `c`
would still have been running, an orphan task nobody awaits.

**Part 2, `return_exceptions=True`**

`d` done at 0.01, `e` fails at 0.02 (no print: the `ValueError` is not a `CancelledError`), `f`
done at 0.03. Then `gather` returns `['d', ValueError('e'), 'f']`: the exception **object**
takes the slot of the failed job, in input order.

**Part 3, `TaskGroup`**

| Time | Event | Printed |
|---|---|---|
| 0 | | `-- taskgroup` |
| 0.01 | `g` succeeds | `g done` |
| 0.02 | `h` raises; the group cancels the unfinished task `i` | |
| | `i` wakes with `CancelledError`, prints, re-raises | `i cancelled` |
| | the group has waited for all; raises `ExceptionGroup([ValueError('h')])` | |
| | `print("after the block")` is skipped: the block raised | |
| | `except* ValueError` matches; `group` is an `ExceptionGroup` | `caught ExceptionGroup ['h']` |
| | | `taskgroup over` |

`i done` is never printed: the TaskGroup's promise is "all succeed, or none are left running".

## Output

```text
-- gather
a done
caught ValueError('b')
c done
gather over
-- return_exceptions
d done
f done
['d', ValueError('e'), 'f']
-- taskgroup
g done
i cancelled
caught ExceptionGroup ['h']
taskgroup over
```

## Complexity

Not relevant: a fixed run of about 0.15 s.

## Another way

Which to use:

- **TaskGroup** when the tasks are parts of one job ("load the page = user + orders +
  settings"). If one part fails, the rest are useless; cancel them and report.
- **`gather(return_exceptions=True)`** when the tasks are independent ("check 100 links") and
  you want every result, good or bad.
- **plain `gather`** rarely: it reports the first error but leaves the siblings running. If you
  use it, cancel the leftovers yourself.

Try changing `i`'s delay to `0.015` in part 3: then `i done` is printed before `h` fails and
nothing is cancelled, but the `ExceptionGroup` is still raised.
