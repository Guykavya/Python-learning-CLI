# Trace grid DP

The "unique paths with obstacles" table of chapter section 8, with a print after every row. `1` is an obstacle, `0` is open; moves go only right or down. Predict **exactly** what this program prints. Do not run it.

```python
grid = [[0, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
        [1, 0, 0, 0]]
rows, cols = len(grid), len(grid[0])
f = [[0] * cols for _ in range(rows)]
for r in range(rows):
    for c in range(cols):
        if grid[r][c] == 1:
            f[r][c] = 0
        elif r == 0 and c == 0:
            f[r][c] = 1
        else:
            up = f[r - 1][c] if r > 0 else 0
            left = f[r][c - 1] if c > 0 else 0
            f[r][c] = up + left
    print(f"row {r}:", f[r])
print("paths:", f[rows - 1][cols - 1])
```

Write your answer in `answer.txt`, one printed line per line: four `row` lines, then the `paths:` line.

## How to work

1. Draw a 4 by 4 table. Mark the two obstacles: row 1 column 2, and row 3 column 0.
2. Fill it row by row, left to right, exactly as the loops do. Each cell is "the cell above + the cell to the left", where a missing neighbour (outside the grid) counts as 0.
3. An obstacle cell is 0, whatever its neighbours hold.
4. Write each row in Python's list format: `[1, 1, 1, 1]`.

## After you answer

1. Row 1, column 3 is 1, although the cell above it is 1 and there is a cell to its left. Why only 1?
2. The bottom-left obstacle sits in the first column. Which cells below or to the right of it lose paths because of it, and which do not?
3. Check the final answer another way: how many right/down paths does a 4 by 4 grid have with no obstacles at all? (Chapter section 8: it is a binomial coefficient.) Is it plausible that two obstacles remove exactly the difference?
