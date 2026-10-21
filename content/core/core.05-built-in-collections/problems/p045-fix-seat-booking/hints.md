## Hint 1

Run the starter on the example and compare line by line. Which wrong lines appear first?
Use `is` to check whether rows, or the seats and the snapshot, are really separate lists.

## Hint 2

Look at every line that **creates** or **copies** a list: the grid, the first snapshot, and
the snapshot in `save`. Which of them make real, independent copies of every row?

## Hint 3

The bugs: `[["."] * cols] * rows` shares one row; `snapshot = seats` is an alias;
`seats.copy()` is shallow; `history.pop(0)` undoes the oldest booking; `seats.count(".")`
counts rows, not seats. Fix with a comprehension for the grid, `[row[:] for row in seats]`
for snapshots, `pop()`, and `sum(row.count(".") for row in seats)`.
