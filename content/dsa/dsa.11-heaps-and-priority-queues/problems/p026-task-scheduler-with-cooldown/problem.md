# Task scheduler with cooldown

A processor runs one task per time unit, or it stays **idle** for that unit. You get a list `tasks` (each item is the name of a task, for example `"A"`) and a number `n >= 0`. Equal names are the same kind of task. The rule: between two runs of the **same** kind of task there must be at least `n` other time units (other tasks or idle units). The tasks may be run in any order.

Write `least_interval(tasks, n)`, which returns the **smallest number of time units** that is needed to run all tasks. With no tasks the answer is `0`.

## Example

```python
>>> least_interval(["A", "A", "A", "B", "B", "B"], 2)
8
>>> least_interval(["A", "A", "A", "B", "B", "B"], 0)
6
>>> least_interval(list("AAAAAABCDEFG"), 2)
16
```

For the first example one best schedule is `A B _ A B _ A B` (`_` is an idle unit): eight units. Between two `A`s there are two other units. With `n = 0` no cooldown exists and six units are enough.

For the third example: six `A`s need `5 * 3 = 15` units between the first and the last `A` plus the last `A` itself: `A _ _ A _ _ A _ _ A _ _ A _ _ A`, which is 16 units; the other six tasks fit into the idle slots (there are 10), so none is added.

## Constraints

- Up to 100,000 tasks; `0 <= n <= 100`. The big tests run in a separate process with a 10-second limit.
- The tests compare your answer with a **search over all schedules** on small inputs, so the answer must be exactly the minimum, not a good guess.

## Think about

Which task is the hardest to place: the one with the most copies left. If you always run the available task with the most copies left, what happens to a task that you just ran? When does it become available again, and what do you run in the meantime? What do you do if nothing is available?

(The chapter does not cover this problem. The hints teach the greedy method with a heap and a waiting queue.)
