## Hint 1

Each generation needs the **old** grid for counting and a **new** grid for writing. How do you
make sure they are different objects?

## Hint 2

Build `new = [["."] * c for _ in range(r)]` (not a copy that shares rows), fill it from `grid`,
then `grid = new`.

## Hint 3

Count neighbours with two loops over `dr` and `dc` in `(-1, 0, 1)`, skipping `(0, 0)` and
positions outside `0 <= i < r`, `0 <= j < c`.
