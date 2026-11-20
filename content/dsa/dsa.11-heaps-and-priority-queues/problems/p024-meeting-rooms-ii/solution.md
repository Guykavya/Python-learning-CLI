## Approach

Sort the meetings by start time and go through them in that order. The heap holds one number per room in use: the **end time of the meeting that is in that room now**. When a new meeting starts, the room that is most likely to be free is the one with the **smallest** end time, which is `heap[0]`:

- if `heap[0] <= start`, that room is free: the new meeting takes it, so replace that end time by the new `end` (`heapreplace`);
- otherwise every room is still busy: open a new room (`heappush`).

The number of rooms is the number of items in the heap at the end (rooms are never closed).

## Code

```python
import heapq

def min_rooms(intervals):
    ends = []
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)           # reuse the room that frees up first
        else:
            heapq.heappush(ends, end)              # open a new room
    return len(ends)
```

`sorted` makes a new list: the caller's list is not touched.

## Complexity

`O(n log n)` time (the sort, plus one heap operation per meeting), `O(n)` memory in the worst case (all meetings overlap).

## Another way

**Sweep line.** Make a list of events: `(start, +1)` and `(end, -1)`, sort it (at equal times the `-1` comes first, because `-1 < +1`, which is exactly the "touching meetings do not overlap" rule), and walk through it while counting how many meetings are on. The answer is the biggest count. Same `O(n log n)`, no heap. Another way: sort the start times and the end times separately and walk through them with two pointers.
