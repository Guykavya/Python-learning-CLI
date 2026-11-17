# A heap of tuples

A **priority queue** hands out the most urgent task first. With `heapq` the usual entry is a tuple `(priority, task)`. But Python compares tuples element by element: when two priorities are **equal**, it compares the tasks, and tasks such as dictionaries cannot be compared (chapter section 5, "the tie-breaker trap").

Write the class

```python
class TaskQueue:
    def add(self, priority, task): ...   # priority: a number, smaller = more urgent
    def pop(self): ...                   # remove and return the TASK (not the priority)
    def __len__(self): ...
```

Rules:

- `pop()` returns the task with the **smallest priority**. Among tasks with the **same** priority the one that was **added first** comes out first (first in, first out).
- The tasks can be **anything**, including dictionaries and plain `object()` instances that cannot be compared with `<`. Your queue must never compare two tasks.
- `pop()` on an empty queue raises `IndexError`.
- Priorities can be ints or floats, negative or not.
- Use `heapq` with tuples of the form `(priority, counter, task)`, where `counter` is a number that grows with every `add`.

## Example

```python
>>> q = TaskQueue()
>>> q.add(2, {"name": "backup"})
>>> q.add(1, {"name": "email"})
>>> q.add(2, {"name": "report"})
>>> q.add(1, {"name": "call"})
>>> [q.pop()["name"] for _ in range(len(q))]
['email', 'call', 'backup', 'report']
```

Without the counter, the second `add(1, ...)` would raise `TypeError: '<' not supported between instances of 'dict' and 'dict'`.

## Constraints

- `add` and `pop` are `O(log n)`. Up to `10**5` operations.
- Do not look inside the tasks and do not change them.

## Think about

Why is the counter placed **between** the priority and the task, and not before the priority or after the task? What would a counter **before** the priority do to the order?
