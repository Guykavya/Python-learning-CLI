## Hint 1

If a run starts at value `x`, what must be true about `x - 1`?

## Hint 2

Put all values in a set. Only start counting from `x` when `x - 1` is **not** in the set; then
count up while `x + 1`, `x + 2`, ... are in the set.

## Hint 3

Each value is counted only as part of the run that starts at its run's first value, so the total
work is O(n). Loop over the **set**, not the list, to skip repeats, and track the best
(length, start), preferring the smaller start on ties.
