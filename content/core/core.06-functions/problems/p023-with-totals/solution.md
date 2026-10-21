## Approach

The danger is the shallow copy. Whatever you do, never call a mutating method on one of the
caller's rows. `row + [sum(row)]` builds a new list per row. Then the column totals are computed
over the new rows, so the last column total is the grand total.

## Code

```python
def with_totals(grid):
    """Return a new grid with a total at the end of each row and a final row of column totals."""
    if not grid:
        return []
    result = [row + [sum(row)] for row in grid]
    totals = [sum(r[j] for r in result) for j in range(len(result[0]))]
    result.append(totals)
    return result
```

## Complexity

O(r × c) for r rows and c columns.

## Another way

`copy.deepcopy(grid)` first, then append freely to the copies. Correct and simple, but it copies
everything even though we only need new rows, and it hides the reason the shallow version fails.
