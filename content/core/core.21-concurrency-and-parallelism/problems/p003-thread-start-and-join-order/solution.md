## Approach

Every ordering is forced, so trace one block at a time:

| Step | Thread | What happens | Printed |
|---|---|---|---|
| 1 | main | `a` created, not started | `created, alive: False` |
| 2 | main | `a.start()`, then `a.join()` waits | |
| 3 | worker-A | `greet("A")` | `A runs in worker-A` |
| 4 | main | join returns; A has finished | `A joined, alive: False` |
| 5 | main | `b.run()` calls `greet("B")` **in the main thread** | `B runs in MainThread` |
| 6 | main | `b` was never started | `after b.run(), alive: False` |
| 7 | main | `c.start()`, then `started.wait()` blocks | |
| 8 | worker-C | prints, sets `started`, blocks in `go.wait()` | `C: started` |
| 9 | main | wakes up; C is blocked but still running its target | `main: C alive? True` |
| 10 | main | main is free to do other work | `main: keeps going while C waits` |
| 11 | main | `go.set()`, then `c.join()` waits | |
| 12 | worker-C | wakes up and finishes | `C: finished` |
| 13 | main | join returned | `main: C alive? False` |
| 14 | main / d | `d` appends `sum(range(5))` = 10; join waits for it | `result from d: [10]` |
| 15 | main | | `end of MainThread` |

Three lessons:

- `start()` runs the target in a new thread; `run()` runs it right here. Step 5 prints
  `MainThread`, and `b.is_alive()` stays `False` because `b` never started.
- A thread **blocked** in `wait()` is still alive. Alive means "its target has not returned".
- A thread cannot return a value through `join()`. Thread `d` hands its result back through a
  shared list, and `join()` is what makes it safe to read: after `join()` the write has
  happened.

Without the `Event`s, lines 8 and 9 could come in either order. That is why real thread code
must never depend on "it usually prints first".

## Output

```text
created, alive: False
A runs in worker-A
A joined, alive: False
B runs in MainThread
after b.run(), alive: False
C: started
main: C alive? True
main: keeps going while C waits
C: finished
main: C alive? False
result from d: [10]
end of MainThread
```
