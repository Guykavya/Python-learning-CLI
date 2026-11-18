## Approach

The heap method of chapter section 6, with one extra field. Process meetings by start time and keep a min-heap of `(end, room)` for the rooms in use. A new meeting reuses the room that frees first if it is already free (`end <= start`, the chapter's rule: a room freed at `t` can be used at `t`); otherwise every room is busy right now, and a new room is opened.

```python
import heapq


def assign_rooms(meetings):
    order = sorted(range(len(meetings)), key=lambda i: meetings[i][0])
    rooms = [0] * len(meetings)
    busy = []                      # min-heap of (end time, room number) for rooms in use
    opened = 0
    for i in order:
        s, e = meetings[i]
        if busy and busy[0][0] <= s:              # the room that frees first is free by now
            _, room = heapq.heappop(busy)
        else:
            room = opened                         # every room is busy: open a new one
            opened += 1
        rooms[i] = room
        heapq.heappush(busy, (e, room))
    return rooms
```

Why the fewest rooms: a new room is opened only when **every** room is busy at this meeting's start, so at that moment `opened` meetings run at once. No assignment can use fewer rooms than the largest number of meetings running together (the lower bound of "interval partitioning"), and this one never uses more.

Ties in the heap: two rooms with the same end time compare by room number, which is always an int, so the tuples never fail to compare.

## Complexity

`O(n log n)`: the sort, plus one push and at most one pop per meeting. `O(n)` space.

## Another way

Keep a second heap of **free room numbers**. Before placing a meeting, move every room whose end is `<= start` from the busy heap to the free heap; then take the smallest free number, or open a new room. It gives the "lowest-numbered free room" rule, which some offices prefer, with the same complexity.
