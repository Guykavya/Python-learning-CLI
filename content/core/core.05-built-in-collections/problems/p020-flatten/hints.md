## Hint 1

Read each line into a list, giving a list of lists. Then flatten.

## Hint 2

`[v for row in rows for v in row]`: the left `for` is the outer loop, just like nested loops.

## Hint 3

For the longest row, loop with `enumerate` and keep the index only when the length is strictly bigger.
