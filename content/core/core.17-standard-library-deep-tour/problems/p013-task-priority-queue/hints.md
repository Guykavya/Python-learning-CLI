## Hint 1

The heap must order by priority first and by push order second. A tuple compares field by field and stops at the first difference. So what should the second field of every pushed tuple be, so that the third field (the task) is never compared?

## Hint 2

Keep a counter in the object: `itertools.count()` gives 0, 1, 2, ... with `next(self._counter)`, or keep an `int` and add 1 on every push. Push `(priority, n, task)`. `pop` returns `heappop(self._heap)[2]`. `peek` looks at `self._heap[0]` (the smallest item of a heap is always at index 0).

## Hint 3

```
class TaskQueue:
    __init__: self._heap = []; self._counter = itertools.count()
    push(task, priority): heappush(self._heap, (priority, next(self._counter), task))
    pop():
        if not self._heap: raise IndexError("pop from an empty TaskQueue")
        return heappop(self._heap)[2]
    peek(): same check, return self._heap[0][2]
    __len__: len(self._heap)
    __bool__: len(self._heap) > 0
```
