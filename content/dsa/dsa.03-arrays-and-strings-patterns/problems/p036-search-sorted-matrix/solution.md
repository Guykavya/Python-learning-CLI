## Approach

From the top-right corner, the current cell is the **largest** of its row-so-far and the **smallest** of its
column-so-far. One comparison with the target therefore removes a whole line:

- value too big: every cell below it in this column is at least as big, so the column cannot hold the target;
- value too small: every cell left of it in this row is at most as big, so the row cannot hold the target.

Each step removes a row or a column, so the walk ends after at most `r + c - 1` steps, either on the target or by
leaving the grid. The path looks like a staircase going down and to the left.

## Code

```python
r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]
q = int(input())
targets = [int(x) for x in input().split()]

out = []
for x in targets:
    i, j = 0, c - 1                  # top-right corner
    found = False
    while i < r and j >= 0:
        v = grid[i][j]
        if v == x:
            found = True
            break
        if v > x:
            j -= 1                   # everything below in this column is even bigger: drop the column
        else:
            i += 1                   # everything left in this row is even smaller: drop the row
    out.append("yes" if found else "no")
print("\n".join(out))
```

Searching 16 in the example: `11` too small (down), `12` too small (down), `16` found at the bottom-right.

## Complexity

O(r + c) per query, O(q * (r + c)) in all, and O(1) extra memory. Scanning every cell is O(r * c) per query.

## Another way

The bottom-left corner works the same way with the directions swapped (too big: move up; too small: move right).
If memory doesn't matter, putting all values into a `set` answers each query in O(1) on average, after O(r * c)
work; the staircase uses no extra memory and also works for questions a set cannot answer, such as "how many
values are at most `x`?".
