## Hint 1

What numbers does `range(1, 4)` produce? For each of them, what numbers does `range(i)` produce?
How many times does the inner loop run when `i` is 1? When `i` is 3?

## Hint 2

Make a table with columns `i`, `j`, `count`, `total` and one row per inner-loop run.
The line `print("row", ...)` runs once per outer round, after the inner loop has finished.

## Hint 3

`range(i)` starts at 0, so `j` takes the values `0, 1, ..., i - 1`.
Every time `j` is 0, `i * j` adds nothing to `total`. Only add the products where `j` is not 0.
