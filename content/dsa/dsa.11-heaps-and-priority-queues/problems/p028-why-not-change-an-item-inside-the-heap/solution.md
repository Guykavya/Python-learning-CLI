## Approach

Start from the rule and not from the code: a heap is a list that obeys "parent `<=` child" everywhere. Every operation of `heapq` assumes that the rule is true and keeps it true. An assignment into the list is not an operation of the heap: Python does not check the rule, so after `heap[3] = 0` the next `heappop` works with a heap that is not one.

## Model answer

See `answer.md`. The three printed lines are:

```text
[1, 2, 3, 4, 5, 7, 8]
[1, 3, 2, 0, 5, 4, 7]
[1, 2, 3, 0, 4, 5, 7]
```

## What to check

- You said what rule is broken **and where** (index 3 below its parent, index 1).
- You said what `heappop` looks at, and why that is not enough to find the problem.
- You gave both ways to change a priority, with their costs.
- You explained why changing the task field of an entry is safe and changing the priority is not.

## Another way

Try it: after `heap[3] = 0`, call `heapq.heapify(heap)` and drain again: the output is sorted. Then try `heapq.heappush(heap, 0)` instead of the assignment (a normal push of the new value) and compare: this is the "lazy" idea, the old `8` is still in the heap.
