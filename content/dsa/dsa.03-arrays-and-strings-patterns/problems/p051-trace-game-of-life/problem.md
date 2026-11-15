# Trace Game of Life neighbour counts

This program runs one generation of the Game of Life (rules: an alive `#` cell with 2 or 3 alive neighbours stays
alive; a dead `.` cell with exactly 3 becomes alive; everything else is dead next time; cells outside the grid are
dead). It prints the **number of alive neighbours** of every cell as a grid of digits, then the next grid. It does
this for two 5 x 5 starting grids. Predict **exactly** what it prints. Do not run it.

```python
def step(grid):
    r, c = len(grid), len(grid[0])
    counts = []
    new = []
    for i in range(r):
        crow = ""
        nrow = ""
        for j in range(c):
            n = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di != 0 or dj != 0) and 0 <= i + di < r and 0 <= j + dj < c:
                        if grid[i + di][j + dj] == "#":
                            n += 1
            crow += str(n)
            if grid[i][j] == "#" and n in (2, 3):
                nrow += "#"
            elif grid[i][j] == "." and n == 3:
                nrow += "#"
            else:
                nrow += "."
        counts.append(crow)
        new.append(nrow)
    print("counts")
    for row in counts:
        print(row)
    print("next")
    for row in new:
        print(row)
    return new


blinker = [".....",
           ".....",
           ".###.",
           ".....",
           "....."]
step(blinker)

glider = [".#...",
          "..#..",
          "###..",
          ".....",
          "....."]
step(glider)
```

Write your answer in `answer.txt`, one line per printed line: `counts`, five digit rows, `next`, five grid rows,
and the same again for the second grid. A digit row looks like `12321`.

## How to work

Use squared paper. Mark the alive cells. For each cell, look at the 3 x 3 block around it, count the `#` in it, and
**do not count the centre**. Cells on the edge have a smaller block: the missing part is outside the grid and is
dead. Fill all 25 digits first, then apply the rules using **both** the digit and whether the cell itself is alive.

## After you answer

1. In the first grid, the middle cell of the row and the cell above it both matter. What are their counts, and why
   does one survive while the other is born?
2. In the second grid, the cell at row 1, column 1 has 5 alive neighbours. Is it alive or dead now, and what happens
   to it?
3. Which counts in the second grid would change if the grid wrapped around (row 4 next to row 0)? Would the next grid
   change?
4. Why must the program read every count from `grid` and write into `new`, instead of changing `grid` as it goes?
