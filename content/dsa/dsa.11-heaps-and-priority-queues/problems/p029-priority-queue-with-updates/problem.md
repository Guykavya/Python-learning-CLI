# Priority queue with updates (lazy deletion)

Write the class `LazyPQ`, a priority queue of **tasks** where a task's priority can be changed and a task can be cancelled. A **smaller** priority number comes out **first**. Use `heapq`, and keep every entry in the heap even when it is out of date (lazy deletion, chapter section 11).

- `add(task, priority)`: put `task` in the queue. If `task` is already in the queue, this **changes** its priority (it is as if the old one was cancelled and a new one added).
- `remove(task)`: cancel `task`. If it is not in the queue, raise `KeyError`.
- `pop()`: remove and return the task with the smallest priority. Tasks with an **equal** priority leave in the order in which they were **last added** (the oldest `add` first; a task whose priority was changed counts as added at the time of the change). If the queue is empty, raise `KeyError`.
- `len(pq)`: the number of tasks in the queue (not the size of the heap list).
- `task in pq`: whether the task is in the queue.
- `pq.stored()`: the number of entries that are in the heap list **at this moment**, including entries that are out of date.

Tasks are hashable (strings, numbers, tuples, plain `object()`s) but **not necessarily comparable with each other**. Priorities are numbers.

## The size rule

Stale entries must not pile up. After **every** call of `add`, `remove` or `pop`, the queue must satisfy

```text
pq.stored() <= 4 * len(pq) + 8
```

so you need to rebuild the heap from the live entries now and then (chapter section 11, "The cost of laziness"). A rebuild costs `O(n)`; do it only when it pays off, so that the cost per operation stays `O(log n)` on average.

## Example

```python
>>> pq = LazyPQ()
>>> pq.add("write", 3); pq.add("test", 2); pq.add("deploy", 1)
>>> pq.add("write", 0)                 # change the priority of "write"
>>> pq.remove("test")
>>> len(pq)
2
>>> pq.pop(), pq.pop(), len(pq)
('write', 'deploy', 0)
>>> pq.add("a", 5); pq.add("b", 5); pq.add("c", 5); pq.add("a", 5)
>>> [pq.pop(), pq.pop(), pq.pop()]     # equal priorities: the oldest add first; "a" was added again last
['b', 'c', 'a']
```

## Constraints

- Up to 100,000 operations. The big tests run in a separate process with a 10-second limit.
- Do not compare tasks. If two entries have the same priority, the heap must still know which one is smaller without looking at the task.

## Think about

Which two things must be in each heap entry besides the task, so that two entries with the same priority never compare the tasks? How do you find the live entry of a task in `O(1)`? What is the cheapest way to say "this entry is dead"? When have "dead" entries become so many that a rebuild pays for itself?
