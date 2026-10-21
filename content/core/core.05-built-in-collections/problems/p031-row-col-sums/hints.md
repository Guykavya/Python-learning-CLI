## Hint 1

Store the grid as a list of row lists. `sum(row)` gives a row total.

## Hint 2

Column `j`'s sum is `sum(row[j] for row in grid)`.

## Hint 3

The grand total is the sum of the row sums (or of the column sums).
