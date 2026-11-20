# Flood fill

The paint-bucket tool of a drawing program: click on a cell, and the whole region of the **same colour** that is connected to it (up, down, left, right) gets the new colour. It is a BFS on the grid graph, where only cells of the old colour are vertices (chapter sections 3 and 5).

Predict **exactly** what this program prints. Do not run it.

```python
from collections import deque

grid = ["aab.",
        "a.ba",
        "aaab",
        "b.ab"]


def flood_fill(grid, r, c, new):
    rows, cols = len(grid), len(grid[0])
    cells = [list(row) for row in grid]
    old = cells[r][c]
    cells[r][c] = new
    queue = deque([(r, c)])
    while queue:
        cr, cc = queue.popleft()
        print(f"visit ({cr}, {cc})")
        for nr, nc in ((cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and cells[nr][nc] == old:
                cells[nr][nc] = new
                queue.append((nr, nc))
    return ["".join(row) for row in cells]


for row in flood_fill(grid, 0, 0, "*"):
    print(row)
```

Write your answer in `answer.txt`, one printed line per line: first one `visit (r, c)` line for every cell taken out of the queue, then the four rows of the new grid.

## How to work

1. Copy the grid onto squared paper and write the row and column numbers around it. The start cell is `(0, 0)`, row first.
2. Keep the queue as a list of cells. A cell is painted (`*`) **when it is put into the queue**, not when it is taken out.
3. For each visited cell, look at its neighbours in the order of the code: up, down, left, right. A neighbour joins the queue only if it is inside the grid and still has the **old** colour `a`.

## After you answer

1. The cell `(1, 3)` is an `a`. Why is it not painted?
2. What would change if the code painted cells only when they are taken out of the queue? Would the final grid change? Could a cell be added to the queue twice?
3. Which neighbour order would make `(0, 1)` the second visited cell?
