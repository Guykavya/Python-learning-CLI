## Approach

Keep the ready queue on paper. A task runs from one pause to the next; `sleep(0)` sends it
to the back; finishing a task sends its waiter to the back.

| Turn | Queue before | Runs | Prints | Pauses at | Queue after |
|---|---|---|---|---|---|
| 1 | (main running) | main | `tasks created` | `sleep(0)` | `[A, B, main]` |
| 2 | `[A, B, main]` | A | `A step 0` | `sleep(0)` | `[B, main, A]` |
| 3 | `[B, main, A]` | B | `B step 0` | `sleep(0)` | `[main, A, B]` |
| 4 | `[main, A, B]` | main | `main after sleep(0)` | `await t1` (A not done) | `[A, B]` |
| 5 | `[A, B]` | A | `A step 1` | `sleep(0)` | `[B, A]` |
| 6 | `[B, A]` | B | `B step 1` | `sleep(0)` | `[A, B]` |
| 7 | `[A, B]` | A | `A done` | returns, so `main` is woken | `[B, main]` |
| 8 | `[B, main]` | B | `B step 2` | `sleep(0)` | `[main, B]` |
| 9 | `[main, B]` | main | `main got A` | `await t2` (B not done) | `[B]` |
| 10 | `[B]` | B | `B done` | returns, `main` woken | `[main]` |
| 11 | `[main]` | main | `main got B`; creates C; `C done? False` | `sleep(0.01)` | `[C]` |
| 12 | `[C]` | C | `C step 0` | `sleep(0)` | `[C]` |
| 13 | `[C]` | C | `C done` | returns | `[]` (main sleeping) |
| 14 | after 0.01 s | main | `C done? True` | ends | |

Lessons:

- **Creating a task does not run it.** A and B only start at `main`'s first pause (turn 1),
  and `C done? False` is printed before C has run a single line.
- Tasks take turns only at `await`s that pause. Between two pauses a task is never
  interrupted, which is why asyncio code needs fewer locks than threaded code.
- `main got A` (turn 9) comes **after** `B step 2` (turn 8): when A finished, B was already
  in the queue in front of `main`.

## Output

```text
tasks created
A step 0
B step 0
main after sleep(0)
A step 1
B step 1
A done
B step 2
main got A
B done
main got B
C done? False
C step 0
C done
C done? True
```

## Complexity

Not relevant for a trace.

## Another way

If `main` did `await asyncio.sleep(0.01)` instead of `sleep(0)` at the start, A and B would
both run to the end (A in 3 turns, B in 4) before `main` printed anything more, because
`sleep(0.01)` keeps `main` out of the ready queue until the timer fires.
