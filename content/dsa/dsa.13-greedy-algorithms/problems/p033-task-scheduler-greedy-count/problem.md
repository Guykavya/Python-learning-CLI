# Task scheduler (greedy count)

A CPU runs tasks, one per time unit. `tasks` is a list of letters; equal letters are the same kind of task. After running a task of some kind, the CPU must wait **at least `n` time units** before running that **same** kind again. In a time unit it can run any other allowed task, or stay **idle**. Tasks can be done in any order.

Write `least_interval(tasks, n)` that returns the **fewest time units** needed to finish all the tasks (idle units included).

This problem is **not** worked in the chapter. It is a greedy with a counting argument: the hints teach a formula, and the "Another way" in the solution shows a simulation with a heap.

## Example

```python
>>> least_interval(["A", "A", "A", "B", "B", "B"], 2)
8
>>> least_interval(["A", "A", "A", "B", "B", "B"], 0)
6
>>> least_interval(["A", "A", "A", "A", "A", "A", "B", "C", "D", "E", "F", "G"], 2)
16
>>> least_interval(["A", "B", "C", "D", "A", "B", "C", "D"], 1)
8
```

The first one: `A B idle A B idle A B`. Every `A` is at least 2 units after the previous `A`, and the same for `B`.

## Constraints

- `0 <= len(tasks) <= 10**5`, letters `"A"`-`"Z"`, `0 <= n <= 100`.
- `O(len(tasks))`: count the letters, then compute. Simulating the schedule is fine for checking, but the answer needs only counts.

## Think about

The most frequent task decides the shape of the schedule. If `A` appears `f` times, at least how long must the schedule be, even if nothing else existed? When can the other tasks fill every gap so that no idle unit is needed at all?
