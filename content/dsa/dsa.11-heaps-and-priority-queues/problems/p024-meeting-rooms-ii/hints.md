## Hint 1

Sort the meetings by their start time. Take the meetings one by one. For the new meeting, ask: is there a room whose current meeting has already ended (end time `<=` the new start)? If yes, the new meeting can use that room. If not, you must open a new room. Which room would you check first to answer the question quickly?

## Hint 2

You do not need to know *which* room: only the **end times of the rooms in use**. The room that frees up first has the smallest end time. Keep these end times in a min-heap. For a new meeting `(start, end)`: if `heap[0] <= start`, replace `heap[0]` by `end` (the room is reused); otherwise push `end` (a new room). The answer at the end is the size of the heap.

## Hint 3

```
ends = []                                  # min-heap of the end times of the rooms in use
for start, end in sorted(intervals):
    if ends and ends[0] <= start:
        heapreplace(ends, end)             # reuse the room that frees up first
    else:
        heappush(ends, end)                # all rooms busy: open a new one
return len(ends)
```

Note the `<=`: a meeting that ends at 5 frees its room for a meeting that starts at 5.
