# heapq: a priority queue with a tie-break counter

A **priority queue** hands out the most urgent item first. With `heapq` you push tuples
`(priority, item)` and pop the smallest. That breaks in two ways when two items have the same
priority:

1. Python then compares the **items** themselves. Two dicts cannot be compared:
   `TypeError: '<' not supported between instances of 'dict' and 'dict'`.
2. Even when the items can be compared, equal-priority items come out in **item** order, not in
   the order they were added. Users expect first come, first served.

The standard fix is a third field in the middle: an always-increasing counter,
`(priority, count, item)`. Counts are never equal, so Python never looks at the item, and an
earlier push wins a tie.

Write a class `TaskQueue` in `solution.py`:

- `push(task, priority: int)`: add a task (any object, often a dict). A **lower** number means more urgent.
- `pop()`: remove and return the most urgent task; among equal priorities, the one pushed first.
  An empty queue raises `IndexError`.
- `peek()`: return the task `pop()` would return, without removing it. Empty: `IndexError`.
- `__len__()` and `__bool__()` (an empty queue is falsy).

**Example**

```python
q = TaskQueue()
q.push({"job": "email"}, 2)
q.push({"job": "backup"}, 1)
q.push({"job": "report"}, 2)
q.pop()     # {'job': 'backup'}
q.pop()     # {'job': 'email'}    pushed before 'report'
len(q)      # 1
```
