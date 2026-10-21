## Approach

Every bug here is about **which objects are shared**. Check each line that builds or copies a
list, and ask: after this line, is there one list or two?

## The bugs

| Line | Bug | Effect |
|---|---|---|
| `seats = [["."] * cols] * rows` | one row object repeated | booking (0, 0) also books (1, 0) |
| `snapshot = seats` | alias, not a copy | the "start" snapshot shows later bookings |
| `snapshot = seats.copy()` | shallow copy | outer list is new, but the rows are shared, so the snapshot still changes |
| `history.pop(0)` | removes the oldest | undo cancels the first booking instead of the latest |
| `seats.count(".")` | counts items of the outer list | the items are rows, never `"."`, so it prints 0 |

## Fixed code

```python
# Cinema seat booking (fixed).
rows, cols = [int(x) for x in input().split()]
seats = [["."] * cols for _ in range(rows)]
snapshot = [row[:] for row in seats]
history = []
while True:
    parts = input().split()
    if parts[0] == "done":
        break
    if parts[0] == "book":
        r, c = int(parts[1]), int(parts[2])
        if seats[r][c] == ".":
            seats[r][c] = "X"
            history.append((r, c))
            print("Booked", r, c)
        else:
            print("Seat", r, c, "is taken")
    elif parts[0] == "undo":
        if history:
            r, c = history.pop()
            seats[r][c] = "."
            print("Undid", r, c)
        else:
            print("Nothing to undo")
    elif parts[0] == "save":
        snapshot = [row[:] for row in seats]
        print("Saved")
print("Seats:")
for row in seats:
    print("".join(row))
print("Free:", sum(row.count(".") for row in seats))
print("Snapshot:")
for row in snapshot:
    print("".join(row))
```

## Why `[row[:] for row in seats]`

A snapshot of a list of lists must copy each row. `seats.copy()`, `list(seats)` and
`seats[:]` copy only the outer list. `copy.deepcopy(seats)` would also work.

## Complexity

Each command is O(1) except `save`, which copies the whole grid: O(rows × cols).
