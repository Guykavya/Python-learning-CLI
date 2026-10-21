## Hint 1

If you copy the outer list with `grid[:]` and then append to each row, whose rows are you appending to?

## Hint 2

Build each new row as `row + [sum(row)]`: `+` creates a new list and leaves `row` alone.

## Hint 3

```
if not grid: return []
result = [row + [sum(row)] for row in grid]
column totals: for each column index j in range(len(result[0])):
    sum(r[j] for r in result)
result.append(totals)
return result
```
Summing the columns of `result` (which already has the row totals) gives the grand total for free.
