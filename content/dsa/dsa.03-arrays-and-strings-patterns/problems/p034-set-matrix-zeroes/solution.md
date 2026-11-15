## Approach

The trap is **reading and writing the same grid in one pass**. Clearing a row and a column immediately creates new
zeros, and the scan later mistakes them for original ones, so zeros spread until the whole grid is wiped.

So separate the two jobs. First record which rows and columns must be cleared, without changing anything. Then
clear them. The marks are two short lists, `r + c` values, instead of a copy of the whole grid.

## Code

```python
r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

# Pass 1: only READ the grid and remember which rows and columns hold an original zero.
zero_row = [False] * r
zero_col = [False] * c
for i in range(r):
    for j in range(c):
        if grid[i][j] == 0:
            zero_row[i] = True
            zero_col[j] = True

# Pass 2: write the zeros. New zeros cannot spread, because pass 1 is finished.
for i in range(r):
    for j in range(c):
        if zero_row[i] or zero_col[j]:
            grid[i][j] = 0

for row in grid:
    print(" ".join(map(str, row)))
```

For the example, pass 1 gives `zero_row = [True, False, True]` and `zero_col = [True, False, True, False]`.
In row 2 only columns 1 and 3 are marked, so `5` and `7` become 0 and `6 8` stay.

## Complexity

O(r * c) time (two passes over the grid) and O(r + c) extra memory. Clearing a row and a column for every zero
costs O(r + c) per zero, up to O(r * c * (r + c)) when there are many zeros.

## Another way

The O(1)-memory trick: use the first row and the first column of the grid itself as the marks. Two extra booleans
remember whether the first row and the first column had zeros of their own. Then clear the inner cells from the
marks, and the first row and column last. It saves memory but is easy to get wrong; the two lists are clearer.
