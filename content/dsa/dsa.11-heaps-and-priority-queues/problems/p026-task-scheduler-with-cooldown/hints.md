## Hint 1

Take `A A A B B B` with `n = 2` and try to write the schedule by hand. After running `A`, when is the next `A` allowed? What do you run in the two units in between? Why is it a good idea to start with a task that has many copies left (`A`, `B`) and not with one that has a single copy?

## Hint 2

Simulate the clock, one time unit per loop turn. Keep:

- a max-heap with the **remaining counts** of the tasks that are available now (negated, as `heapq` is a min-heap);
- a queue `cooling` of the tasks that were just run and wait, as `(time_when_available, remaining_count)`. It is first in, first out, because tasks become available in the order they were run.

In every unit: first move from `cooling` to the heap every task whose time has come. Then, if the heap is not empty, run the task with the largest remaining count (take one copy; if copies remain, put it in `cooling`). If the heap is empty, the unit is idle.

## Hint 3

```
heap = [-count for each kind of task]; heapify
cooling = empty queue           # items (available_at, remaining negative count)
time = 0
while heap or cooling:
    time += 1
    while cooling and cooling[0].available_at <= time:
        push(heap, cooling.popleft().count)
    if heap:
        count = pop(heap) + 1              # one copy done (counts are negative)
        if count < 0:
            cooling.append((time + n + 1, count))
return time
```

A task run at time `t` is available again at time `t + n + 1` (there are `n` units in between).
