## Hint 1

Take the meetings in order of **start time**. When a meeting starts, which room should it take? If some room is already free, any free room works; the simplest is the one whose last meeting **ended first**. If no room is free, you must open a new one. How do you find "the room that frees first" quickly?

## Hint 2

Keep a min-heap of pairs `(end_time, room)` for the rooms in use. `busy[0]` is the room that frees first. If `busy[0][0] <= start` (equal is fine: the room freed at that very moment), pop it and reuse that room; otherwise open room number `opened` and add 1 to `opened`. Then push `(end, room)`.

To answer in **input** order, sort the **indices** `0 .. n-1` by start time (chapter section 5 sorts indices the same way) and write `rooms[i]`.

## Hint 3

```
order = indices sorted by meetings[i].start
rooms = [0] * n; busy = []; opened = 0
for i in order:
    s, e = meetings[i]
    if busy and busy[0].end <= s:  room = heappop(busy).room
    else:                          room = opened; opened += 1
    rooms[i] = room
    heappush(busy, (e, room))
return rooms
```
