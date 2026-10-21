# Add totals without touching the input

Write `with_totals(grid)` for a list of rows of numbers. It returns a **new** grid where:

- each row has its row total appended, and
- one extra final row holds the column totals (including the grand total at the end).

The caller's grid, **and every inner row**, must be left exactly as they were.

**Example**

```python
g = [[1, 2],
     [3, 4]]
with_totals(g)
# [[1, 2, 3],
#  [3, 4, 7],
#  [4, 6, 10]]
g          # still [[1, 2], [3, 4]]
```

An empty grid (no rows) returns `[]`. All rows have the same length.
